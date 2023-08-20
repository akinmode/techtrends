#!/usr/bin/env python3

FROM python:3.8

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 3111

RUN python init_db.py

CMD [ "python", "app.py" ]
