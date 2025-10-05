FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools

RUN pip install uv \
    && uv pip compile pyproject.toml -o requirements.txt \
    && pip install --no-cache-dir -r requirements.txt \
    && ldconfig \
    && rm -rf /root/.cache/pip

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD [ "executable" ]

CMD ["python", "playground.py"]
