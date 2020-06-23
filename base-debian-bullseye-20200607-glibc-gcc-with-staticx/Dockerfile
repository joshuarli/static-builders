FROM base-debian-bullseye-20200607-glibc-gcc

RUN apt-get install -y --no-install-recommends \
    python3-pip \
    python3-setuptools \
    patchelf

# This is temporary until staticx releases the fix to https://github.com/JonathonReinhart/staticx/issues/132.
RUN python3 -m pip \
        --disable-pip-version-check --no-cache-dir install \
    'https://test-files.pythonhosted.org/packages/f5/65/cc5e23b63ddef8aa3b28d5457bfda3c1ff4bdd660236fb431102ee506e8b/staticx-0.10.0.346-py3-none-any.whl'
