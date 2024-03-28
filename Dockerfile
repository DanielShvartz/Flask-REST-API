# Use the python 3.10 image
# IF ANY ISSUES OCCURE - SLIM, MOVE TO FULL VERSION
FROM python:3.10-slim

# We will use the port 5000 on the host so we expose that port
EXPOSE 5000

# set the current dir as app instead of running cd, then if the folder doesnt exist it will be created
WORKDIR /app

# install dependencies
# instead of installing flask each build we store it in a txt file which is cached. if a change occures it will rebuilt.
COPY requirements.txt .
RUN pip install -r requirements.txt && rm -rf /var/lib/lists/*

# copy directory files to the container directory - in this case - /app
COPY . .

# run flask with the ip of the host so it can be accessible
CMD ["flask", "run", "--host", "0.0.0.0"]