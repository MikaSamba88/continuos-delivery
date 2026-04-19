FROM python:3.14-alpine AS deploy
WORKDIR /api
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .
ENTRYPOINT ["fastapi", "run", "main.py", "--port", "8000"]

FROM python:3.14-alpine AS test
WORKDIR /api
COPY requirements.txt .
COPY test_requirements.txt .
RUN pip install -r requirements.txt
RUN pip install -r test_requirements.txt
COPY main.py .
COPY test_main.py .
ENTRYPOINT sh


