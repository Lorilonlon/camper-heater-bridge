FROM public.ecr.aws/docker/library/alpine:3.22 AS build
RUN apk add --no-cache gcc musl-dev bluez-dev
COPY truma_security_delay.c /src/truma_security_delay.c
COPY tests /src/tests
RUN gcc -Wall -Wextra -Werror -o /src/test-security /src/tests/test_security_delay.c -ldl && /src/test-security
RUN gcc -shared -fPIC -nostdlib -fno-stack-protector -Wall -Wextra -Werror \
    -Wl,-z,relro,-z,now -o /src/security-delay.so /src/truma_security_delay.c
FROM public.ecr.aws/docker/library/python:3.13-alpine3.22
RUN pip install --no-cache-dir dbus-next==0.2.3
COPY --from=build /src/security-delay.so /app/security-delay.so
COPY main.py apply.sh remove.sh LICENSE /app/
CMD ["python", "-u", "/app/main.py"]
