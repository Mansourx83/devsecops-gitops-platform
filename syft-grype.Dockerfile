FROM alpine:3.19

RUN apk add --no-cache \
    curl \
    ca-certificates \
    bash \
    jq \
    util-linux

# Install Syft
RUN curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | \
    sh -s -- -b /usr/local/bin

# Install Grype
RUN curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | \
    sh -s -- -b /usr/local/bin

RUN syft --version && \
    grype --version && \
    jq --version && \
    column --version

CMD ["sh"]