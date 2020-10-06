FROM base-debian-bullseye-20200607-glibc-gcc

# Don't care about layer size.
RUN apt-get install -y --no-install-recommends \
    python3-minimal \
    python3-pip \
    python3-setuptools \
    patchelf

RUN python3 -m pip \
        --disable-pip-version-check \
        --no-cache-dir \
    install \
        'staticx==0.12.0'
