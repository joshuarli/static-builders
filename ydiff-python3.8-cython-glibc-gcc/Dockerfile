FROM base-debian-bullseye-20200607-glibc-gcc-with-staticx

RUN apt-get install -y --no-install-recommends \
    python3-dev \
    && rm -rf /var/lib/apt/lists

# Only needed if I'm regenerating ydiff.c, but I chose to check it in the repo.
# RUN python3 -m pip \
#         --disable-pip-version-check --no-cache-dir install \
#         Cython
# RUN cython --embed -3 -D --fast-fail ydiff

COPY src /build
WORKDIR /build

# XXX: Even if you add -static and -lpthread -lz -lm -lexpat -ldl,
# (which python3-config --libs gets wrong!!!)
# You run into the inevitable glibc static linking errors e.g.
# warning: Using 'getservbyport' in statically linked applications requires at runtime the shared libraries from the glibc version used for linking
# The silly part is, we're not doing any networking...
# This is coming from the giant big dumb python3.8 static lib:
# /usr/bin/ld: /usr/lib/gcc/x86_64-linux-gnu/9/../../../x86_64-linux-gnu/libpython3.8.a(socketmodule.o)
# So clearly there's a lot more room for improvement.
RUN gcc -O3 -flto ydiff.c \
    -I/usr/include/python3.8 \
    -lpython3.8 \
    -o ydiff

# Unfortunately, this doesn't produce a working static binary. :(
# RUN staticx --no-compress ydiff-compiled ydiff \
#     && strip -s ydiff
