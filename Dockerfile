FROM alpine:3.12

COPY . .

RUN set -e \
  && rm -rf .git \
  && apk --no-cache add python3 py3-pip \
  && ln -s /usr/bin/python3 /usr/bin/python \
  && apk --no-cache add --virtual .build-deps build-base python3-dev libffi-dev \
  && pip install --no-cache-dir -r requirements.txt \
  && apk del .build-deps

CMD ["python", "-u", "main.py"]
