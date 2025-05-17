from config import get_settings
from fastapi import APIRouter

import logging

logger = logging.getLogger("logger")

router = APIRouter()

@router.get('/status/ping')
async def get_status():
    logger.info("Status information")
    return {
        "message": {"status": "pong"}
    }

@router.get('/app/version')
async def get_version():
    logger.info("Version information")
    return {
        "message": {"version": get_settings().version}
    }