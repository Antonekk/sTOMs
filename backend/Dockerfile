FROM python:3.12-slim


# Set env values for python 
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app


RUN apt-get update \
    && apt-get install -y --no-install-recommends netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#
COPY ./startapp.sh .
RUN chmod +x /app/startapp.sh

COPY . .

ENTRYPOINT ["/app/startapp.sh"]
