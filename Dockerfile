FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /uvx /bin/

WORKDIR /up/

COPY pyproject.toml .python-version uv.lock ./
RUN uv sync --no-cache

FROM base AS app

RUN apt-get update && apt-get install cron -y
COPY . ./

COPY ./crontab /etc/cron.d/
RUN chmod 0644 /etc/cron.d/crontab

RUN crontab /etc/cron.d/crontab

RUN touch /var/log/cron.log

CMD ["cron", "-f"]

FROM base AS testing

RUN apt-get update && apt-get install --no-install-recommends -y make curl git libatomic1
COPY . ./
