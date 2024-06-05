import asyncio
from datetime import datetime, timedelta
from typing import Optional

import loguru
import uvicorn
from fastapi import FastAPI, HTTPException
from loguru import logger
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.chat_worker import ChatWorker
from src.config import Settings, get_config, logger_set_up
from src.fill_db_with_data import Filler
from src.models.chat_model import ChatModel
from src.models.message import Message
from src.routes import common, mongo_routes


async def app_startup():
    """Signal from fastapi"""
    log: loguru.Logger = loguru.logger.bind(object_id='Startup')
    log.info("app_startup")

    if settings.debug_mode:
        loop = asyncio.get_running_loop()  # start new async loop for asyncio
        loop.set_debug(True)  # for more precise errors and tracebacks


def normal_app():
    """ Construct fastapi app object with all routes """
    fastapi_app = FastAPI(version='0.1', title='MongoDB Work')

    fastapi_app.add_event_handler(event_type='startup', func=app_startup)

    # fastapi_app.include_router(common.router)
    # fastapi_app.include_router(mongo_routes.router)

    @fastapi_app.post("/chat/add_test_data/{num_of_chats}")
    async def add_test_data(num_of_chats: int = 3):
        results = []
        f = Filler(settings)
        chats = f.generate_chats(num_of_chats)
        logger.debug(f'chats len: {len(chats)}')
        chat_worker.chats.insert_many(chats)
        # res, msg = await chat_worker.add_member(chat_id, member)
        failure_flag = True if None in results else False
        if not failure_flag:
            return JSONResponse(content={"message": f"{num_of_chats} chats added successfully"})
        else:
            return JSONResponse(status_code=404, content='One of operations raised error!')

    # region Chat
    # region Chat CRUD
    @fastapi_app.post("/chat")
    async def create_chat(chat: ChatModel):
        chat_id = await chat_worker.add_chat(chat)
        return JSONResponse(content={"chat_id": chat_id})

    @fastapi_app.get("/chat/{chat_id}")
    async def view_chat(chat_id: str):
        chat = await chat_worker.view_chat_by_id(chat_id)
        if chat:
            return chat
        else:
            return JSONResponse(status_code=404, content="Chat not found")

    @fastapi_app.put("/chat/{chat_id}/name")
    async def change_chat_name(chat_id: str, name: str):
        chat = await chat_worker.change_chat_name(chat_id, name)
        if chat.modified_count == 1:
            return JSONResponse({"message": "Chat name updated successfully"})
        else:
            return JSONResponse(status_code=404, content="Chat not found")

    # endregion Chat CRUD

    @fastapi_app.post("/chat/{chat_id}/member")
    async def add_member(chat_id: str, member: int):
        res, msg = await chat_worker.add_member(chat_id, member)
        if res:
            return JSONResponse(content={"message": "Member added successfully"})
        else:
            return JSONResponse(status_code=404, content=msg)

    @fastapi_app.post("/chat/{chat_id}/message")
    async def add_message(chat_id: str, message: Message):
        # TODO: add check if message sender is present in chat at the moment
        chat = await chat_worker.add_message(chat_id, message)
        if chat.modified_count == 1:
            return JSONResponse(content={"message": "Message added successfully"})
        else:
            return JSONResponse(status_code=404, content="Chat not found")

    @fastapi_app.delete("/chat/{chat_id}")
    async def delete_chat(chat_id: str):
        res = await chat_worker.delete_chat(chat_id)
        if res:
            return JSONResponse(content={"message": res[1]})
        else:
            return JSONResponse(status_code=404, content=res[1])

    # endregion Chat

    # region Common

    @fastapi_app.get("/config")
    async def config() -> JSONResponse:
        """ Returns all settings of service """
        # здесь мне нужно обратится к settings:
        return JSONResponse(content=settings.model_dump())
        # return JSONResponse(content=settings)

    @fastapi_app.get("/diag")
    async def diag() -> JSONResponse:  #
        """ Standard /diag route """

        delta = datetime.now() - start_time
        if delta.days < 0:  # for midnight
            delta = timedelta(
                days=0,
                seconds=delta.seconds,
                microseconds=delta.microseconds
            )

        # uptime calculations
        td_sec = delta.seconds  # getting seconds field of the timedelta
        hour_count, rem = divmod(td_sec, 3600)  # calculating the total hours
        minute_count, second_count = divmod(rem, 60)  # distributing the remainders
        delta = f"{delta.days}:{hour_count}:{minute_count}:{second_count}"

        # global tv
        response = {
            "res"    : "ok",
            "app"    : f'{settings.service_name}',
            "version": f'{settings.version}',
            "uptime" : delta,
            # "test_value": tv
        }

        # tv += 1
        # test_value += 1
        return JSONResponse(content=response)

    @fastapi_app.middleware('http')
    async def mdlwr(request: Request, call_next):
        """
        Middleware это предобработчик запросов
        :param request: Запрос входящий
        :param call_next: Следующий ендпоинт, куда в оригинале шел запрос
        """
        # logger: loguru.Logger = loguru.logger.bind(object_id='Middleware')
        req_start_time = datetime.now()
        # вывести адрес ручки без адреса и порта сервиса
        logger.debug(f"Incoming request: /{''.join(str(request.url).split('/')[3:])}")
        response = await call_next(request)
        process_time = (datetime.now() - req_start_time)
        response.headers["X-Process-Time"] = str(process_time)
        logger.debug(f'Request time took {process_time} seconds')
        return response

    @fastapi_app.exception_handler(404)
    async def custom_404_handler(request: Request, exc: HTTPException):
        """Собственный обработчик 404 ошибки"""

        content = {
            "res": "Error",
            "msg": f"Not found {request.method} API handler for {request.url}",
            "err": repr(exc),
        }
        logger.debug(f"content={content}")
        return JSONResponse(content=content,
                            status_code=404)

    # endregion Common

    return fastapi_app


def main():
    global app
    global settings
    global start_time
    global chat_worker

    print(f'main')
    settings = get_config()  # Глобальная переменная settings
    logger_set_up(settings)  # set ip logger
    logger.info(f'Logger up!')
    start_time = datetime.now()
    chat_worker = ChatWorker(settings)  # create chat worker

    app = normal_app()  # create fastapi app
    # app.settings = settings  # add settings to app

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
    settings: Settings = None
    start_time: datetime = None
    chat_worker: ChatWorker = None
    app: FastAPI = None
    main()
