FROM python:3.12-slim AS builder

WORKDIR /app
COPY Requirements.txt .
RUN pip install --no-cache-dir -r Requirements.txt

COPY app/ ./app/
COPY tests/ ./tests/

# Run tests during build — if tests fail, Docker build fails too!
RUN python -m pytest tests/ -v --tb=short

FROM python:3.12-slim AS production

WORKDIR /app
COPY Requirements.txt .
RUN pip install --no-cache-dir flask==3.0.3
COPY app/ ./app/
#  sdfghjk
# Non-root user for security
RUN useradd -m appuser
USER appuser
 
EXPOSE 5000
 

 
CMD ["python", "app/main.py"]