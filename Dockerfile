FROM python:3-alpine

LABEL maintainer="Patrice Ferlet <metal3d@gmail.com>"
RUN set -xe ;\
    pip3 install requests

ADD update.py /update.py
USER 1001
CMD ["/update.py"]
