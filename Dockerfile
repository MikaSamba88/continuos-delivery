FROM python:3.14-alpine AS deploy
WORKDIR /api

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .
ENTRYPOINT ["fastapi", "run", "main.py", "--port", "8000"]

# ---TEST STAGE---
FROM python:3.14-alpine AS test
WORKDIR /api

COPY src/requirements.txt .
COPY tests/test_requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r test_requirements.txt

COPY src/ ./src/ 
COPY tests/ ./tests/

COPY tests/.coveragerc .

ENTRYPOINT ["sh"]


