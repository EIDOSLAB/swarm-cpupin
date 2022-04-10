FROM python:3.9.12-slim

RUN pip install docker

COPY src /app
WORKDIR /app

ENTRYPOINT [ "/app/main.py" ]