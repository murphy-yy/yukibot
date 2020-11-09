FROM ubuntu:focal

WORKDIR /app

COPY . .

RUN set -e \
    \
    && apt-get update \
    && apt-get install -y --no-install-recommends python3-pip youtube-dl ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    \
    && pip3 install -r requirements.txt

CMD ["python3", "-u", "main.py"]
