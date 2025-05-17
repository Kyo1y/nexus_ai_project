"""
Source code adapted from https://github.com/cozodb/openai-multi-client
"""

import asyncio
import logging

import openai

from threading import Thread
from typing import Any, Optional

from aioprocessing import AioJoinableQueue, AioQueue
from tenacity import wait_random_exponential, stop_after_attempt, AsyncRetrying, RetryError

from application.openai_manager.payload import Payload

logger = logging.getLogger(__name__)

class OpenAIMultiClient:
    def __init__(self,
                 concurrency: int = 10,
                 max_retries: int = 3,
                 timeout: float = 40,
                 wait_interval: float = 0,
                 retry_multiplier: float = 1,
                 retry_max: float = 60,
                 endpoint: Optional[str] = None,
                 data_template: Optional[dict] = None,
                 metadata_template: Optional[dict] = None,
                 custom_api=None):
        self._endpoint = endpoint
        self._wait_interval = wait_interval
        self._timeout = timeout
        self._data_template = data_template or {}
        self._metadata_template = metadata_template or {}
        self._max_retries = max_retries
        self._retry_multiplier = retry_multiplier
        self._retry_max = retry_max
        self._concurrency = concurrency
        self._loop = asyncio.new_event_loop()
        self._in_queue = AioJoinableQueue(maxsize=concurrency)
        self._out_queue = AioQueue(maxsize=concurrency)
        self._event_loop_thread = Thread(target=self._run_event_loop)
        self._event_loop_thread.start()
        self._mock_api = custom_api
        for i in range(concurrency):
            asyncio.run_coroutine_threadsafe(self._worker(i), self._loop)

    def run_request_function(self, input_function, *args, stop_at_end=True, **kwargs):
        if stop_at_end:
            def f(*args, **kwargs):
                input_function(*args, **kwargs)
                self.close()
        else:
            f = input_function
        input_thread = Thread(target=f, args=args, kwargs=kwargs)
        input_thread.start()

    def _run_event_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _process_payload(self, payload: Payload) -> Payload:
        logger.debug(f"Processing {payload.metadata['prompt_name']} using endpoint \"{payload.endpoint}\"")
        if self._mock_api:
            payload.response = await self._mock_api(payload)
        elif payload.endpoint == "completions":
            payload.response = await openai.Completion.acreate(**payload.data)
        elif payload.endpoint == "chat.completions" or payload.endpoint == "chats":
            payload.response = await openai.ChatCompletion.acreate(**payload.data)
        elif payload.endpoint == "embeddings":
            payload.response = await openai.Embedding.acreate(**payload.data)
        elif payload.endpoint == "edits":
            payload.response = await openai.Edit.acreate(**payload.data)
        elif payload.endpoint == "images":
            payload.response = await openai.Image.acreate(**payload.data)
        elif payload.endpoint == "fine-tunes":
            payload.response = await openai.FineTune.acreate(**payload.data)
        else:
            raise ValueError(f"Unknown endpoint {payload.endpoint}")
        logger.debug(f"Processed {payload.metadata['prompt_name']}")
        return payload

    async def _worker(self, i):
        while True:
            payload = await self._in_queue.coro_get()

            if payload is None:
                # logger.debug(f"Exiting worker {i}")
                self._in_queue.task_done()
                break

            try:
                async for attempt in AsyncRetrying(
                        wait=wait_random_exponential(multiplier=payload.retry_multiplier, max=payload.retry_max),
                        stop=stop_after_attempt(payload.max_retries)):
                    with attempt:
                        try:
                            payload.attempt = attempt.retry_state.attempt_number
                            payload = await asyncio.wait_for(self._process_payload(payload), self._timeout)
                            await self._out_queue.coro_put(payload)
                            self._in_queue.task_done()
                        except asyncio.TimeoutError:
                            logger.warning(f'Request for {payload.metadata["prompt_name"]} took longer than {self._timeout:.0f} seconds, killed request.')
                            raise
                        except openai.error.Timeout:
                            logger.warning(f'OpenAI sent back timeout error on request for {payload.metadata["prompt_name"]}')
                            raise
                        except Exception as e:
                            logger.exception(f"Error processing async payload {payload.metadata['prompt_name']} ({str(e)})")
                            raise
            except RetryError as e:
                payload.failed = True
                await self._out_queue.coro_put(payload)
                self._in_queue.task_done()

                if isinstance(e.last_attempt.exception(), asyncio.exceptions.TimeoutError):
                    logger.error(f'Failed to get response from OpenAI in {self._timeout} after {payload.max_retries} attempts. Timeout triggered from client side.')
                elif isinstance(e.last_attempt.exception(), openai.error.Timeout):
                    logger.error(f'Failed to get response from OpenAI in {self._timeout} after {payload.max_retries} attempts. Timeout triggered from OpenAI side.')
                else:
                    logger.exception(f"Failed to process {payload.metadata['prompt_name']}")

            await asyncio.sleep(self._wait_interval)

    def close(self):
        try:
            for i in range(self._concurrency):
                self._in_queue.put(None)
            self._in_queue.join()
            self._out_queue.put(None)
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._event_loop_thread.join()
        except Exception as e:
            logger.error(f"Error closing: {e}")

    def __iter__(self):
        return self

    def __next__(self):
        out = self._out_queue.get()
        if out is None:
            raise StopIteration
        out.call_callback()
        return out

    def request(self,
                data: dict,
                endpoint: Optional[str] = None,
                metadata: Optional[dict] = None,
                callback: Any = None,
                max_retries: Optional[int] = None,
                retry_multiplier: Optional[float] = None,
                retry_max: Optional[float] = None):
        payload = Payload(
            endpoint=endpoint or self._endpoint,
            data={**self._data_template, **data},
            metadata={**self._metadata_template, **(metadata or {})},
            callback=callback,
            max_retries=max_retries or self._max_retries,
            retry_multiplier=retry_multiplier or self._retry_multiplier,
            retry_max=retry_max or self._retry_max
        )
        self._in_queue.put(payload)

    def pull_all(self):
        responses = []
        for i in self:
            responses.append(i.__dict__)
        return responses
    