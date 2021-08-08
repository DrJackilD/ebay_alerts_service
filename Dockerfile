FROM python:3.9-slim-buster

COPY requirements/common.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
WORKDIR /app
COPY .docker_env .env
COPY ./ebay_alerts_service ./ebay_alerts_service
COPY manage.py .
EXPOSE 8000

ENTRYPOINT ["python", "manage.py"]
CMD ["run"]
