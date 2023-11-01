FROM bitnami/python:3.8

WORKDIR /usr/src/app
USER root

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]
