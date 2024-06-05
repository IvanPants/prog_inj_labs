from pydantic import BaseModel, Field


class Settings(BaseModel):
    """ Pydantic model to validate settings """

    service_name: str = 'BFA - Big Fucking Application'
    version: str = "0.3"
    self_api_host: str = '0.0.0.0'  # fastapi address
    self_api_port: int = 8080  # fastapi port


    # postgres
    postgres_user: str = 'ivan'  # задается в docker-compose
    postgres_pass: str = 'ivan'  # задается в docker-compose

    # postgres_host: str = '172.19.0.2'  #
    # postgres_host: str = 'localhost'  # in docker container
    postgres_host: str = 'postgres_db'  # in docker-compose
    # postgres_host: str = 'localhost'  # in docker-compose
    postgres_port: int = 5432  # задан в docker-compose
    # postgres_name: str = 'users_db'  # задан в docker-compose
    postgres_name: str = 'users_db'  # задан в docker-compose

    postgres_connection_timeout: int = 3
    postgres_str: str = ''

    # mongo
    # mongo_host: str = '127.0.0.1'    # no docker
    mongo_host: str = '172.17.0.2'  # in docker container
    # TODO: try localhost for mongo_host
    mongo_port: int = 27017
    mongo_name: str = 'mongo_work'

    # формат и цвета логов
    log_format: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>[<level>{level}</level>]" \
                      "<cyan>[{extra[object_id]}]</cyan>" \
                      "<magenta>{function}</magenta>:" \
                      "<cyan>{line}</cyan> - <level>{message}</level>"

    debug_mode: bool = True


if __name__ == '__main__':
    model = Settings()
    print(model)
