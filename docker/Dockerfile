FROM python:3.13.0rc2-slim

RUN pip install --upgrade pip
RUN apt update && apt install -y jq yq
# Installing this version to address security vulnerability reported in CVE-2024-33599
# This line should come out once the fix is included in a python image.
RUN apt install -y libc-bin
RUN useradd -m cortex
ADD config /home/cortex/.cortex/config 

RUN python -m pip install cortexapps-cli

WORKDIR /home/cortex
USER cortex

ENTRYPOINT ["cortex"]
