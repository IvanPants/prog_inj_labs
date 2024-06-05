from pydantic import BaseModel


class Settings(BaseModel):
    """ Pydantic model to validate settings """
    service_name: str = 'MongoDB Work'
    version: str = "0.1"
    # self_api_host: str = '0.0.0.0'
    self_api_host: str = '0.0.0.0'
    self_api_port: int = 7007

    # db_host: str = '127.0.0.1'
    db_host: str = 'mongo'
    db_port: int = 27017
    db_name: str = 'mongo_work'

    # формат и цвета логов
    log_format: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>[<level>{level}</level>]" \
                      "<cyan>[{extra[object_id]}]</cyan>" \
                      "<magenta>{function}</magenta>:" \
                      "<cyan>{line}</cyan> - <level>{message}</level>"

    debug_mode: bool = True
