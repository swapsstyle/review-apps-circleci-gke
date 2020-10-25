# Author: Anil Saravade
# Copyright: Copyright (©) 2020. SwapStyle. All rights reserved.

FROM python:3.7.9-alpine

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt

COPY hook.py /app/hook.py

ENTRYPOINT [ "python3" ]
