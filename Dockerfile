FROM python:3.11.3
RUN mkdir -p /opt/
WORKDIR /opt/
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# docker build -t django-app:v1.0.0 .
# docker run --name django-app -p 8000:8000 django-app:v1.0.0