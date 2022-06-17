FROM python:3.8-alpine3.14

COPY ./crontab /var/spool/cron/crontabs/root

RUN pip install gspread oauth2client

ENV TZ=America/Sao_Paulo

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

CMD crond -l 2 -f && tail -f /var/log/cron.log