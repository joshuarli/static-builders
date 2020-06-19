FROM base-alpine-3.12-musl-gcc

RUN apk add --no-cache \
    bash

# Alpine 3.12 doesn't have a libimagequant-static, so we must build it ourselves.
COPY libimagequant-2.12.6 /build-libimagequant-2.12.6
WORKDIR /build-libimagequant-2.12.6
RUN make static

RUN apk add --no-cache \
    libpng-dev \
    libpng-static \
    zlib-static

COPY src /build
WORKDIR /build
RUN CFLAGS="-O3 -static -flto" \
    ./configure \
        --with-libimagequant=/build-libimagequant-2.12.6 \
    && make \
    && strip -s ./pngquant
