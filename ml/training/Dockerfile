FROM python:3.12-slim
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY train.py generate_data.py ./
COPY data ./data
CMD ["uv", "run", "python", "train.py"]
