FROM ubuntu:latest
MAINTAINER Vitaly Lazebnikh 'labvit@gmail.com'
RUN apt-get update -y
RUN apt-get install -y python3-pip python-dev build-essential
COPY . /app
WORKDIR /app 
RUN pip install -r requirements.txt
CMD /usr/bin/python3 /app/app.py

