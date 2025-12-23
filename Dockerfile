# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
# (Make sure to generate requirements.txt first: pip freeze > requirements.txt)
# Minimal requirements included inline for convenience:
RUN pip install --no-cache-dir \
    numpy scipy matplotlib torch pandas streamlit fastapi uvicorn pydantic

# Copy App Code
COPY . .

# Permissions
RUN chmod +x start.sh

# Expose Ports (API + Dashboard)
EXPOSE 8000
EXPOSE 8501

# Entrypoint
ENTRYPOINT ["./start.sh"]
