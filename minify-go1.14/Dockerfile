FROM golang:1.14.4-alpine3.12

COPY src /build
WORKDIR /build
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags '-s -w' .
