FROM alpine:3.13.0

COPY . .

RUN set -e \
  && rm -rf .git \
  && apk --no-cache add python3 py3-pip ffmpeg \
  && ln -s /usr/bin/python3 /usr/bin/python \
  && apk --no-cache add --virtual .build-deps build-base python3-dev libffi-dev \
  && pip install --no-cache-dir -r requirements.txt \
  && apk del .build-deps

ENV PYTHONUNBUFFERED 1

ENTRYPOINT ["python", "main.py"]
