FROM python:3.9-slim-bullseye

RUN apt-get update && \
    apt-get -qq -y install tesseract-ocr && \
    apt-get -qq -y install libtesseract-dev

WORKDIR /app

COPY . .

RUN chmod +x build.sh

CMD ["./build.sh"]
