FROM python:3.5-alpine

RUN pip install pip pipenv

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY Pipfile Pipfile.lock /usr/src/app/
RUN pipenv install --system --deploy

COPY . /usr/src/app/

CMD python .
