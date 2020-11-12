FROM python:3.7-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory

WORKDIR /yaas-project-2019-masinde70
COPY requirements.txt /yaas-project-2019-masinde70/


# Install dependencies
RUN apt-get update && apt-get install -y gettext libgettextpo-dev
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt


# Copy project

COPY . /yaas-project-2019-masinde70/