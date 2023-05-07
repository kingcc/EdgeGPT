FROM docker.io/library/python:3.11.3-alpine3.16@sha256:0ba61d06b14e5438aa3428ee46c7ccdc8df5b63483bc91ae050411407eb5cbf4 AS builder

WORKDIR /EdgeGPT

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN apk add --no-cache make
RUN make init
RUN make build
RUN make ci
RUN apk del make
RUN rm -Rf /root/.cache/pip

EXPOSE 5000

ENV FLASK_APP=server.py

CMD ["flask", "run", "--host=0.0.0.0"]