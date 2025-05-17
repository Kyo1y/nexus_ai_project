from config import get_settings
from fastapi import FastAPI
from log import LogConfig
from logging.config import dictConfig
from routers import main_router, data_analysis_router

import logging
import uvicorn


dictConfig(LogConfig().dict())
logger = logging.getLogger("logger")

api = FastAPI(
    title = get_settings().title,
    version = get_settings().version
)

api.include_router(main_router.router, prefix="/api/v1")
api.include_router(data_analysis_router.router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "main:api", 
        host="0.0.0.0", 
        port=get_settings().port, 
        log_level="debug",
        debug=True
    )