FROM base-debian-bullseye-20200607-glibc-gcc

RUN apt-get install -y --no-install-recommends \
    bash \
    libpng-dev \
    zlib1g-dev \
    libimagequant-dev \
    && rm -rf /var/lib/apt/lists

COPY src /build
WORKDIR /build
RUN CFLAGS="-O3 -flto -pipe" LDFLAGS="-static" ./configure
RUN make -j"$(nproc)" \
    && strip -s ./pngquant
