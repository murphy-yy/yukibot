FROM alpine:3.12

COPY . /app

WORKDIR /app

RUN set -e \
	&& apk --no-cache add py3-pip py3-yarl ffmpeg \
	&& pip install -r requirements.txt

ENV PYTHONUNBUFFERED 1

CMD ["python3", "main.py"]
