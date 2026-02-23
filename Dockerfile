FROM python:3.14-alpine

WORKDIR /app

COPY age_sweeper/ ./age_sweeper/

ENTRYPOINT ["python", "-m", "age_sweeper"]
