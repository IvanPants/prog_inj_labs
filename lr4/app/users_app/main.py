import uvicorn
from fastapi import FastAPI
from loguru import logger

from src.database import Base, engine
from src.config import get_config, logger_set_up
from src.routers import router
from src.settings_model import Settings


def main():
    global app
    settings: Settings = get_config()
    logger_set_up(settings)
    logger.info(f'Logger up!')
    logger.info(f'{settings.service_name} running on {settings.self_api_host}:{settings.self_api_port}')

    app = FastAPI(
        title=f"{settings.service_name}",
        version=settings.version,
        description=f"Documentation for {settings.service_name}:{settings.version}",
        docs_url="/"
    )

    app.include_router(router, prefix="/user", tags=["user"])

    Base.metadata.create_all(bind=engine)

    try:
        # disabled duplicate logs (uvicorn logs)
        # uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
        # del uvicorn_log_config["loggers"]

        uvicorn.run(app=f'__main__:app',
                    host=settings.self_api_host,
                    port=settings.self_api_port,
                    log_level="debug", access_log=False)

    except KeyboardInterrupt:
        logger.warning("KEYBOARD INTERRUPT MAIN")
    except Exception as e:
        logger.error("MAIN ERROR", f"e: {repr(e)}")


if __name__ == '__main__':
    app: FastAPI = None
    main()
