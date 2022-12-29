FROM alpine:3.14

### Environment Variables ###
ENV APP_NAME=python_rotating_relay_proxy_server
# Needed for pycurl
ENV PYCURL_SSL_LIBRARY=openssl

# Install dependencies
RUN apk add --no-cache python3 sqlite tor

# Install temp dependencies
RUN apk add --no-cache --virtual .build-dependencies build-base curl-dev libcurl libressl-dev python3-dev py3-pip gcc wget curl

# Create and copy required files and directories
RUN mkdir -p /$APP_NAME
RUN mkdir -p /etc/tor
COPY requirements.txt /$APP_NAME/requirements.txt
COPY torrc /etc/tor/torrc

WORKDIR /$APP_NAME

RUN pip install -r requirements.txt 

# RUN apk --purge del .build-dependencies

CMD ["tor", "-f", "/etc/tor/torrc"]
