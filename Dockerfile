FROM python:3.11.3
RUN mkdir -p /opt/
WORKDIR /opt/
COPY . .
RUN pip install -r requirements.txt --no-cache-dir
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# 直接构建执行
# docker build -t django-app:v1.0.0 .
# docker run --name django-app -p 8000:8000 django-app:v1.0.0

# 下面是推送仓库
# docker tag django-app:v1.0.0 harbor地址/组名/django-app:v1.0.0
# docker push harbor地址/组名/django-app:v1.0.0