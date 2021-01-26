FROM debian:latest
MAINTAINER Yassir Laaouissi
WORKDIR /app

COPY . /app

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install git openjdk-11-jdk chromium chromium-driver -y
RUN apt install -y gcc g++ python3 python3-pip python3-dev python3-wheel ffmpeg libxslt
RUN pip3 install -r requirements.txt
RUN pip3 install --upgrade git+https://github.com/yunusemrecatalcam/twint.git@twitter_legacy2

CMD ["python3", "2hrs.py"]



