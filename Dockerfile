# syntax=docker/dockerfile:1

FROM debian:bookworm-slim

ARG DEBIAN_FRONTEND=noninteractive
ARG WINE_BRANCH=stable
ARG WINE_VERSION=""
ARG LTSPICE_MSI_URL="https://ltspice.analog.com/software/LTspice64.msi"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        wget \
        gnupg \
        locales \
        xvfb \
        cabextract \
        winbind \
        p7zip-full \
        unzip \
        python3 \
        python3-pip \
        python3-venv \
        git \
        chafa \
        librsvg2-bin \
        fonts-dejavu-core \
        fontconfig \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    WINEDEBUG=-all \
    WINEPREFIX=/tmp/wine-prefix \
    HOME=/tmp/claw-home

RUN dpkg --add-architecture i386 \
    && mkdir -p /etc/apt/keyrings \
    && wget -qO /etc/apt/keyrings/winehq.key https://dl.winehq.org/wine-builds/winehq.key \
    && echo "deb [signed-by=/etc/apt/keyrings/winehq.key] https://dl.winehq.org/wine-builds/debian/ bookworm main" > /etc/apt/sources.list.d/winehq.list \
    && apt-get update \
    && if [ -n "${WINE_VERSION}" ]; then \
        apt-get install -y --no-install-recommends \
          winehq-${WINE_BRANCH}=${WINE_VERSION} \
          wine-${WINE_BRANCH}=${WINE_VERSION} \
          wine-${WINE_BRANCH}-amd64=${WINE_VERSION} \
          wine-${WINE_BRANCH}-i386=${WINE_VERSION}; \
      else \
        apt-get install -y --no-install-recommends winehq-${WINE_BRANCH}; \
      fi \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 claw \
    && useradd -m -u 1000 -g 1000 -s /bin/bash claw \
    && mkdir -p /tmp/claw-home \
    && chmod 1777 /tmp/claw-home

USER claw
WORKDIR /home/claw
RUN Xvfb :99 -screen 0 1024x768x24 >/tmp/xvfb-install.log 2>&1 & \
    sleep 2 \
    && DISPLAY=:99 WINEPREFIX=/home/claw/.wine WINEDLLOVERRIDES="mscoree,mshtml=" wineboot --init \
    && WINEPREFIX=/home/claw/.wine wineserver --wait \
    && wget -q -O /tmp/LTspice64.msi "${LTSPICE_MSI_URL}" \
    && DISPLAY=:99 WINEPREFIX=/home/claw/.wine wine msiexec /i /tmp/LTspice64.msi /quiet /norestart \
    && WINEPREFIX=/home/claw/.wine wineserver --wait \
    && rm -f /tmp/LTspice64.msi \
    && pkill Xvfb || true

USER root
RUN mv "/home/claw/.wine/drive_c/Program Files/ADI/LTspice" /opt/ltspice \
    && ln -s /opt/ltspice "/home/claw/.wine/drive_c/Program Files/ADI/LTspice" \
    && mv /home/claw/.wine /opt/wineprefix-template \
    && find /opt/ltspice -type d -exec chmod a+rwx {} + \
    && find /opt/ltspice -type f -exec chmod a+rw {} + \
    && find /opt/wineprefix-template -type d -exec chmod a+rwx {} + \
    && find /opt/wineprefix-template -type f -exec chmod a+rw {} +

WORKDIR /workspace
COPY pyproject.toml README.md LICENSE NOTICE.md ./
COPY src ./src
RUN python3 -m pip install --break-system-packages --no-cache-dir ".[runtime,docs,dev]"

COPY docker/entrypoint.sh /usr/local/bin/claw-spice-entrypoint
COPY docker/ltspice /usr/local/bin/ltspice
RUN chmod +x /usr/local/bin/claw-spice-entrypoint /usr/local/bin/ltspice

USER claw
ENTRYPOINT ["/usr/local/bin/claw-spice-entrypoint"]
CMD ["claw-spice", "doctor"]
