import sys
from app.utils.logging_helper import logger
from fastapi import FastAPI
import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.utils.config_helper import get_config
from app.api.api_v1 import account, task

import ssl


# Load app configuration
cfg = get_config()


async def on_startup():
    logger.info(f'Starting {cfg.app.title}')


async def on_shut_down():
    logger.info(f'Shutting down {cfg.app.title}')


# init app lifecyle
@asynccontextmanager
async def lifespan(app: FastAPI):
    await on_startup()
    yield
    await on_shut_down()


# Init fastapi
app = FastAPI(    
    lifespan=lifespan,
    title=cfg.app.title,
    version=cfg.app.version,
    description=cfg.app.description,
    contact={
        'name': cfg.app.developer_name,
        'url': cfg.app.developer_repo_url,
        'email': cfg.app.developer_email
    }
)


# add middleware
app.add_middleware(
    CORSMiddleware,    
    allow_origins=["*"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=['application/json', 'authorization', 'x-refresh-token'],
)

# Create ssl context
logger.info("Creating ssl context")
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

# Load ssl cert and key
logger.info("Loading tls cert.pem and key.pem files")
ssl_context.load_cert_chain(certfile=cfg.app.tls_cert_path, keyfile=cfg.app.tls_key_path)

# Include user authentication routes
app.include_router(account.router)

# Include task management routes
app.include_router(task.router)



if __name__ == "__main__":
    try:
        uvicorn.run(cfg.app.entry_point, host=cfg.app.host, port=cfg.app.port, reload=cfg.app.reload, lifespan=cfg.app.lifespan, ssl=ssl_context)
    except KeyboardInterrupt as e:
        logger.warning(f'Stopping {cfg.app.title} server due to keyboard interuption')
        sys.exit(1)