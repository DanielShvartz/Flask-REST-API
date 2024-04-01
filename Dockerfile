# Deployment
#FROM python:3.10-slim
#WORKDIR /app
#COPY requirements.txt .
#RUN pip install -r requirements.txt && rm -rf /var/lib/lists/*
#COPY . .
#RUN flask db upgrade
#CMD ["/bin/bash", "docker-entrypoint.sh"] 

# Local
FROM python:3.10-slim
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt && rm -rf /var/lib/lists/*
COPY . .
RUN flask db upgrade
CMD ["flask", "run", "--host", "0.0.0.0"]