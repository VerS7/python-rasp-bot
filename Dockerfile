FROM python:3.11.11-alpine as builder

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY . .

RUN python -m venv /app/.venv

RUN apk update --no-cache && apk add tzdata

RUN pip install --upgrade pip --no-cache-dir

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11.11-alpine

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

COPY . .
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /usr/share/zoneinfo/Europe/Moscow /usr/share/zoneinfo/Europe/Moscow

ENV TZ="Europe/Moscow"

ENTRYPOINT [ "python", "main.py" ]