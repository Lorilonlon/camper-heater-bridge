FROM public.ecr.aws/docker/library/python:3.13-alpine3.22
ARG BUILD_VERSION=0.1.0
ARG BUILD_ARCH=aarch64
LABEL io.hass.version="$BUILD_VERSION" io.hass.type="app" io.hass.arch="$BUILD_ARCH"
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bridge ./bridge
COPY LICENSE /app/LICENSE
ENV PYTHONUNBUFFERED=1 DBUS_SYSTEM_BUS_ADDRESS=unix:path=/run/dbus/system_bus_socket
CMD ["python", "-m", "bridge.main"]
