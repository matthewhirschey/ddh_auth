FROM python:3.8.5-alpine

WORKDIR /usr/src/app
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Collect static files.
RUN mkdir static && DJANGO_ALLOWED_HOSTS='localhost' SECRET_KEY=DUMMY python manage.py collectstatic --noinput

CMD ./run.sh
