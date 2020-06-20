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
    python3-pip \
    patchelf

RUN python3 -m pip \
        --disable-pip-version-check --no-cache-dir install \
    setuptools \
    staticx

RUN apt-get install -y --no-install-recommends \
    ca-certificates \
    curl

WORKDIR /build

RUN curl -sL https://github.com/libvips/libvips/releases/download/v8.9.2/vips-8.9.2.tar.gz | tar -xz -f- --strip-components=1 -C .

# TODO: Add --disable-deprecated
# Blocked by https://github.com/libvips/libvips/pull/1593

# XXX: -static doesn't work here, I'm using staticx to
# make the final vips binary static... although, it doesn't seem to work either:
# ./vips-glibc-gcc jpegsave
# .staticx.prog: unknown action "/tmp/staticx-BPJkll/.staticx.prog"
RUN CFLAGS="-O3 -flto -pipe" CXXFLAGS="-O3 -flto -pipe" \
    ./configure \
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
    && staticx vips ../vips
