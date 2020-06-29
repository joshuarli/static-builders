FROM base-debian-bullseye-20200607-glibc-gcc-with-staticx

RUN apt-get install -y --no-install-recommends \
    ca-certificates \
    curl

WORKDIR /build
# TODO: 8.10 release is coming soon. I think they're gonna use libspng.
# This doesn't actually work, because they don't check in configure, it has to be generated.
# It's not easy to avoid pulling in gtkdocize and a bunch more autostuff libtool stuff, so... guess we'll just have to wait.
RUN curl -sL https://github.com/libvips/libvips/archive/e1a4b98be9975e2c0484970ab20ad3571a64beaa.tar.gz | tar -xz -f- --strip-components=1 -C . \
    && apt-get purge -y --auto-remove \
        ca-certificates \
        curl

RUN apt-get install -y --no-install-recommends \
    g++ \
    libglib2.0-dev \
    libexpat1-dev \
    libjpeg-dev \
    libpng-dev \
    libimagequant-dev \
    libexif-dev \
    liborc-0.4-dev \
    && rm -rf /var/lib/apt/lists

# XXX: -static doesn't work here. I'm using staticx to make the final vips binary static.
# Could also try clang.
RUN CFLAGS="-O3 -flto -pipe" CXXFLAGS="-O3 -flto -pipe" \
    ./configure \
        --disable-deprecated \
        --disable-shared \
        --disable-static \
        --disable-dependency-tracking

# This is the fastest easiest way I found to compile the
# CLI as fast as possible. You can probably get more optimal,
# but it'd be a lot harder wrestling autotools.
RUN cd libvips \
    && make -j"$(nproc)"
RUN cd tools \
    && make -j"$(nproc)" vips

RUN cd tools \
    && staticx vips ../vips \
    && strip -s ../vips
