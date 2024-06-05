FROM python:3.11.7-slim
MAINTAINER IVAN PANZYRNYI

# часовой пояс
ENV TZ=Europe/Moscow
ENV PYTHON_VERSION 3.11.7
# pyc файлы не генерить - включаем, тк все равно менять код внутри контейнера без перезапуска не получится
ENV PYTHONDONTWRITEBYTECODE 1
# JIC. Display logs and dont wait for buffer to fill. Maybe loguru flushes buffer on its own, idk.
ENV PYTHONUNBUFFERED 1

WORKDIR /opt/mongo_work

COPY . .

RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# вручную обьявить порт
EXPOSE 7007

# add rights to execute files
RUN chmod +x run_mongo_app.py

CMD ["python", "run_mongo_app.py"]