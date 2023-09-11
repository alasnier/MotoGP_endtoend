FROM python:3.9
#FROM python:3.9-alpine
# FROM python:3.9-slim

WORKDIR /home/app

RUN apt-get update -y
RUN apt get upgrade -y 

COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

COPY . /home/app

CMD python scraper.py 