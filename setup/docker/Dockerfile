# Author: Anil Saravade
# Copyright: Copyright (©) 2020. SwapStyle. All rights reserved.

FROM ubuntu:18.04
RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev && \
    pip3 install flask
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt
COPY ./hook.py /app
ENTRYPOINT [ "python3" ]
CMD [ "hook.py" ]