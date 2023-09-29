# Set the working directory
# FROM python:3.9
# FROM python:3.9-alpine
FROM python:3.9-slim

WORKDIR /home/app

# Update the package manager and install necessary packages
RUN apt-get update -y && apt-get install -y curl
RUN pip install --upgrade pip

# Install gcloud SDK 
RUN curl -sSL https://sdk.cloud.google.com | bash
# Add gcloud to PATH
ENV PATH $PATH:/root/google-cloud-sdk/bin

# Copy & Install requirements
COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

# Copy service account key 
COPY service-account-key.json /service-account-key.json
# Set the environment variable to point to the service account key file (if using a service account key)
ENV GOOGLE_APPLICATION_CREDENTIALS=/service-account-key.json

# Authenticate using the service account key or user credentials
RUN gcloud auth activate-service-account --key-file=/service-account-key.json

# Set the default project (if necessary)
RUN gcloud config set project motogp-project-398408

COPY . /home/app

# Clean up unnecessary files and packages
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD python scraper.py 