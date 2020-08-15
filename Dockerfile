FROM alpine:3.12

COPY . /app

WORKDIR /app

RUN set -e \
	&& apk --no-cache add \
		py3-pip \
		ffmpeg \
	&& apk --no-cache add --virtual .build-deps \
		libffi-dev \
		build-base \
		python3-dev \
	&& pip install -r requirements.txt \
	&& apk --no-cache del .build-deps

ENV PYTHONUNBUFFERED 1

CMD ["python3", "main.py"]
