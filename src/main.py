from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import logging

from database.database import create_db_and_tables
from parse_hh import load_area_resolver_from_file, load_metro_resolver_from_file
from config import configure_logging

from auth import router as auth_router
from templates import router as templates_router
from parse_hh import router as parse_hh_router
from api import router as api_router



configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.area_resolver = load_area_resolver_from_file("parse_hh/areas.json")
    logger.info('преобразователь areas в id загружен')
    
    app.state.metro_resolver = load_metro_resolver_from_file("parse_hh/metro.json")
    logger.info('преобразователь metro в id загружен')

    await create_db_and_tables()
    yield


app = FastAPI(title='parser_hh', lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(templates_router)
app.include_router(parse_hh_router)
app.include_router(api_router)