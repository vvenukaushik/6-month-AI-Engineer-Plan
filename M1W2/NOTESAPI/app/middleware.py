import time, logging
from fastapi import Request

logger = logging.getLogger("notes_api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")

async def logging_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    ms = round((time.time() - start) * 1000)
    logger.info(f"{request.method} {request.url.path} {response.status_code} {ms}ms")
    return response