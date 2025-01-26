FROM python:3.12-bookworm

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY requirements_linux.txt /tmp/requirements_linux.txt

ARG BUILD_ARCH=amd64
RUN apt update                                                                                                                                         

RUN pip install -r /tmp/requirements_linux.txt \
    && pip install setuptools \                                                                                                                    
    && apt-get purge -y --auto-remove \
    && apt-get clean \
    && rm -fr \
        /tmp/* \
        /var/{cache,log}/* \
        /var/lib/apt/lists/*

COPY startup.sh /usr/local/bin
RUN chmod +x /usr/local/bin/startup.sh

ENTRYPOINT ["/usr/local/bin/startup.sh"]

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

# Labels
LABEL \
    maintainer="David Vanhoucke <vanhouckedavid@gmail.com>" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.vendor="Timmo" \
    org.opencontainers.image.authors="Aidan Timson <aidan@timmo.dev>" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://system-bridge.timmo.dev" \
    org.opencontainers.image.source="https://github.com/${BUILD_REPOSITORY}" \
    org.opencontainers.image.documentation="https://github.com/${BUILD_REPOSITORY}/blob/master/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}
