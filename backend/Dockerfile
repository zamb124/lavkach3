FROM python:3.11

RUN mkdir /fastapi

WORKDIR /fastapi

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

#RUN chmod a+x docker/*.sh

WORKDIR src
CMD PWD
CMD gunicorn --bind 0.0.0.0:8000 -w 4 -k uvicorn.workers.UvicornWorker app.server:app