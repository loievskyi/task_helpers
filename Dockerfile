FROM python:3.12
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN python -m pip install -r requirements.txt
RUN pip uninstall -y redis || true
RUN pip install --no-cache-dir redis==6.4.0
COPY . .
