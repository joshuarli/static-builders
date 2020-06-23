FROM base-debian-10-glibc-gcc

RUN apt-get install -y --no-install-recommends \
    ca-certificates \
    curl

RUN apt-get install -y --no-install-recommends \
    libc-dev \
    automake

WORKDIR /build

RUN curl -sL https://github.com/kohler/gifsicle/archive/v1.92.tar.gz | tar -xz -f- --strip-components=1 -C .

RUN autoreconf -i \
    && CFLAGS="-O3 -flto -pipe" LDFLAGS="-static" ./configure \
        --disable-gifview \
        --disable-gifdiff \
        --disable-dependency-tracking

RUN make -j"$(nproc)" \
    && mv src/gifsicle . \
    && strip -s ./gifsicle
