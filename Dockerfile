FROM python:3.14-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . .


CMD ["sh","-c","gunicorn Tracker.wsgi.application -w 2 -b 0.0.0.0:${PORT:-8000}"]