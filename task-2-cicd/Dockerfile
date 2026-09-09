FROM python:3.13-alpine AS base

RUN apk upgrade --no-cache libuuid


FROM base AS build

WORKDIR /build

COPY app.py test_app.py ./

RUN python -m unittest -v
RUN mkdir /out && cp app.py /out/app.py


FROM base AS runtime

# A named account makes the existing non-root identity explicit.
RUN addgroup -S -g 10001 app \
    && adduser -S -D -H -u 10001 -G app -s /sbin/nologin app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Keep application code owned by root; the app user only needs to read it.
COPY --from=build /out/app.py ./app.py

USER 10001:10001

EXPOSE 8080

CMD ["python", "app.py"]
