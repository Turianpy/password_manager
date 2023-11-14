FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN python manage.py makemigrations && python manage.py migrate

COPY . .

ENV PYTHONPATH .

CMD ["gunicorn", "password_manager.wsgi:application", "--bind", "0:8000", "--workers", "3", "--reload"]