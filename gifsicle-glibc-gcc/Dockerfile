FROM base-debian-bullseye-20200607-glibc-gcc

RUN apt-get install -y --no-install-recommends \
    libc-dev \
    automake \
    && rm -rf /var/lib/apt/lists

COPY src /build
WORKDIR /build

RUN autoreconf -i \
    && CFLAGS="-O3 -flto -pipe" LDFLAGS="-static" ./configure \
        --disable-gifview \
        --disable-gifdiff \
        --disable-dependency-tracking

RUN make -j"$(nproc)" \
    && mv src/gifsicle . \
    && strip -s ./gifsicle
