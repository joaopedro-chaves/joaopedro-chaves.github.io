FROM golang:1.24-alpine

# Instala dependências necessárias para o Hugo Extended e módulos Go
RUN apk add --no-cache git curl bash build-base libc6-compat libstdc++ gcompat

# Instalação do Hugo Extended
ARG HUGO_VERSION=0.145.0
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then HUGO_ARCH="linux-amd64"; \
    elif [ "$ARCH" = "aarch64" ]; then HUGO_ARCH="linux-arm64"; \
    else HUGO_ARCH="linux-amd64"; fi && \
    curl -L -o /tmp/hugo.tar.gz "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_${HUGO_ARCH}.tar.gz" && \
    tar -xzf /tmp/hugo.tar.gz -C /tmp && \
    mv /tmp/hugo /usr/local/bin/hugo && \
    rm -rf /tmp/*

WORKDIR /src

EXPOSE 8000

CMD ["hugo", "server", "--bind", "0.0.0.0", "-p", "8000", "--logLevel", "debug", "--disableFastRender", "--buildDrafts"]
