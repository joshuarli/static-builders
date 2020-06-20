FROM base-debian-10-glibc-gcc

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
