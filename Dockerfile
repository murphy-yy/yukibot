FROM python:3

COPY . .

RUN set -e \
 && apt-get -y update \
 && apt-get -y install ffmpeg \
 && pip install -r requirements.txt

CMD ["python", "-u", "main.py"]
