FROM alpine:3.12

RUN apk add --no-cache \
        gcc \
        musl-dev \
        make \
    && rm \
        /usr/libexec/gcc/x86_64-alpine-linux-musl/9.3.0/cc1obj \
        /usr/libexec/gcc/x86_64-alpine-linux-musl/9.3.0/d21

# If you don't need LTO, this shaves off another ~16 MB:
# rm /usr/libexec/gcc/x86_64-alpine-linux-musl/9.3.0/lto1 && \
# rm /usr/libexec/gcc/x86_64-alpine-linux-musl/9.3.0/lto-wrapper && \
