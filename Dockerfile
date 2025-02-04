FROM python:3.11.11-alpine AS builder

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY . .

RUN python -m venv /app/.venv

RUN apk update && apk add tzdata

RUN pip install --upgrade pip 

RUN pip install -r requirements.txt

FROM python:3.11.11-alpine

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

COPY . .
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /usr/share/zoneinfo/Europe/Moscow /usr/share/zoneinfo/Europe/Moscow

RUN apk update --no-cache && apk add --no-cache ca-certificates

ENV TZ="Europe/Moscow"

ENTRYPOINT [ "python", "./src/main.py" ]