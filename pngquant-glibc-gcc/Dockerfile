FROM debian:10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    make \
    pkg-config

RUN apt-get install -y --no-install-recommends \
    bash \
    libpng-dev \
    zlib1g-dev \
    libimagequant-dev

COPY src /build
WORKDIR /build
RUN CFLAGS="-O3 -static -flto" \
    ./configure \
    && make \
    && strip -s ./pngquant
