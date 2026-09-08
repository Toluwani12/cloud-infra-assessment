FROM python:3.13-slim AS build

WORKDIR /build

COPY app.py test_app.py ./

RUN python -m unittest -v
RUN mkdir /out && cp app.py /out/app.py


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=build /out/app.py ./app.py

USER 10001:10001

EXPOSE 8080

CMD ["python", "app.py"]