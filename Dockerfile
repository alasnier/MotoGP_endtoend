# Set the working directory
# FROM python:3.9
# FROM python:3.9-alpine
FROM python:3.9-slim

WORKDIR /home/app

# Update the package manager and install necessary packages
RUN apt-get update -y && apt-get install -y curl
RUN pip install --upgrade pip

# Copy & Install requirements
COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

COPY . /home/app

# Clean up unnecessary files and packages
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD python scraper.py ; python aws.py