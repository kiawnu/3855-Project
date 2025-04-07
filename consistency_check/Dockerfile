FROM python:3

LABEL maintainer="kabdollahi@my.bcit.ca"

RUN mkdir /app
RUN mkdir -p /app/data
RUN mkdir -p /app/logs
RUN mkdir -p /app/config
RUN mkdir -p /app/stats

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

RUN chown -R nobody:nogroup /app
USER nobody

EXPOSE 8400

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]