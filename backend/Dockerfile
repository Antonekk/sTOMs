FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/entrypoint.sh /app/scripts/entrypoint.sh
RUN chmod +x /app/scripts/entrypoint.sh

COPY . .

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["gunicorn", "stoms.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
