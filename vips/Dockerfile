FROM base-debian-glibc-gcc-staticx AS builder

# Don't care about layer caching, because I'm only using docker for building.
RUN apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    g++ \
    g++-10 \
    libglib2.0-dev \
    libexpat1-dev \
    libjpeg-dev \
    libpng-dev \
    libimagequant-dev \
    libexif-dev \
    liborc-0.4-dev \
    && rm -rf /var/lib/apt/lists

# TODO: Vendored source to remove test/ and doc/ with patches to remove test/ from configure.
#       This would also remove the need to install ca-certificates + curl.

# TODO: libspng build with meson, miniz to replace libpng-dev.
# https://github.com/randy408/libspng/blob/master/docs/build.md#meson
# Then, publish the final image somewhere.

WORKDIR /build
RUN curl -sL https://github.com/libvips/libvips/releases/download/v8.10.1/vips-8.10.1.tar.gz | \
    tar -xz -f- --strip-components=1

# XXX: -static doesn't work here. I'm using staticx to make the final vips binary static.
# Could also try clang.
# TODO: webp support
RUN CFLAGS="-O2 -flto -pipe" CXXFLAGS="-O2 -flto -pipe" \
    ./configure \
        --disable-deprecated \
        --disable-shared \
        --disable-static \
        --disable-dependency-tracking \
        --disable-gtk-doc

# This is the fastest easiest way I found to compile the
# CLI as fast as possible. You can probably get more optimal,
# but it'd be a lot harder wrestling autotools.
RUN cd libvips \
    && make -j"$(nproc)"

RUN cd tools \
    && make -j"$(nproc)" vips

RUN cd tools \
    && staticx vips /bin/vips \
    && strip -s /bin/vips

FROM scratch
COPY --from=builder /bin/vips /bin/vips
# This is a nice hack to mkdir /tmp in a scratch image.
WORKDIR /tmp/
ENTRYPOINT ["/bin/vips"]
CMD ["--help"]
