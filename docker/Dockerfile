FROM python:3.13-slim

RUN pip install --upgrade pip
RUN apt update && apt upgrade -y && apt install -y jq yq
RUN useradd -m cortex
ADD config /home/cortex/.cortex/config 

RUN python -m pip install cortexapps-cli

WORKDIR /home/cortex
USER cortex

ENTRYPOINT ["cortex"]
