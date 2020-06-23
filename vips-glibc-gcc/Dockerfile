FROM base-debian-bullseye-20200607-glibc-gcc

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
    python3-setuptools \
    patchelf

# This is temporary until staticx releases the fix to https://github.com/JonathonReinhart/staticx/issues/132.
RUN python3 -m pip \
        --disable-pip-version-check --no-cache-dir install \
    'https://test-files.pythonhosted.org/packages/f5/65/cc5e23b63ddef8aa3b28d5457bfda3c1ff4bdd660236fb431102ee506e8b/staticx-0.10.0.346-py3-none-any.whl'
WORKDIR /build

RUN curl -sL https://github.com/libvips/libvips/releases/download/v8.9.2/vips-8.9.2.tar.gz | tar -xz -f- --strip-components=1 -C .

# TODO: Add --disable-deprecated
# Blocked by https://github.com/libvips/libvips/pull/1593
# XXX: LDFLAGS="-static" doesn't work here. I'm using staticx to make the final vips binary static.
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
    && staticx vips ../vips \
    && strip -s ../vips
