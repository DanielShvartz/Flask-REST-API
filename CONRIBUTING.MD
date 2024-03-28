# CONTRIBUTING

## dockerfile for local running:
```
FROM python:3.10-slim
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt && rm -rf /var/lib/lists/*
COPY . .
RUN flask db upgrade
CMD ["flask", "run", "--host", "0.0.0.0"]
```
## To run the command:
```
docker run --name store_api -p 5000:5000 -it -v ${PWD}:/app store_api
```