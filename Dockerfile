FROM python:3.8.5

COPY . /app

WORKDIR /app

RUN set -e \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
  ffmpeg \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 \
 && pip install -r requirements.txt

ENV PYTHONUNBUFFERED 1

CMD ["python", "main.py"]
