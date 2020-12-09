from . import tableau
from fastapi import FastAPI
from app.settings import settings
from fastapi_cache import caches, close_caches
from fastapi.middleware.cors import CORSMiddleware
from tableauhyperapi import HyperProcess, Telemetry
from fastapi_cache.backends.redis import CACHE_KEY, RedisCacheBackend

HYPER_PROCESS_CACHE_KEY = "HYPER_PROCESS"

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup() -> None:
    # Connect to redis cache
    rc = RedisCacheBackend(settings.redis_cache_url)
    caches.set(CACHE_KEY, rc)

    # Check if Hyper Process has started
    # Note: Doing this in order to ensure only one
    # Hyper process is started.
    if not caches.get(HYPER_PROCESS_CACHE_KEY):
        caches.set(
            HYPER_PROCESS_CACHE_KEY,
            HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU),
        )

@app.on_event("shutdown")
async def on_shutdown() -> None:
    await close_caches()

    # Check if hyper process is running and shut it down
    process: HyperProcess = caches.get(HYPER_PROCESS_CACHE_KEY)
    if process:
        print("Shutting down hyper process")
        process.close()


# Include separate routes
app.include_router(tableau.router)