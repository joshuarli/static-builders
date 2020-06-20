FROM base-debian-10-glibc-gcc

RUN apt-get install -y --no-install-recommends \
    g++ \
    libglib2.0-dev \
    libexpat1-dev \
    libjpeg-dev \
    libpng-dev \
    libimagequant-dev \
    libexif-dev \
    liborc-0.4-dev

RUN apt-get install -y --no-install-recommends \
    ca-certificates \
    curl

WORKDIR /build

RUN curl -sL https://github.com/libvips/libvips/releases/download/v8.9.2/vips-8.9.2.tar.gz | tar -xz -f- --strip-components=1 -C .

# TODO: --disable-deprecated
# Blocked by https://github.com/libvips/libvips/pull/1593

# XXX: This doesn't actually produce a static tools/vips, lol.
RUN CFLAGS="-O3 -static -flto" CXXFLAGS="-O3 -static -flto" \
    ./configure

# TODO: is there an easy way to only compile the CLI?
# I feel like it's compiling way more than it should.

RUN make -j"$(nproc)" \
    && mv tools/vips .
