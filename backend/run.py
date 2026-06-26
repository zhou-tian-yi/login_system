import uvicorn
from urllib.parse import urlparse
from config import settings, LOGGING_CONFIG

url = urlparse(settings.SERVICE_URL)
host = url.hostname or "127.0.0.1"
port = url.port or 8000

if __name__ == "__main__":
    uvicorn.run("main:app", host=host, port=port, log_config=LOGGING_CONFIG)
