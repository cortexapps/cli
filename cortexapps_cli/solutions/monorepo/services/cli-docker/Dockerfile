FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install cortexapps-cli

ENTRYPOINT ["cortex"]
CMD ["--help"]
