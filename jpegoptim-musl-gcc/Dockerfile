FROM base-alpine-3.12-musl-gcc

RUN apk add --no-cache \
    libjpeg-turbo-dev libjpeg-turbo-static

COPY src /build
WORKDIR /build
RUN CFLAGS="-O3 -static -flto" ./configure \
    && make \
    && strip -s ./jpegoptim
