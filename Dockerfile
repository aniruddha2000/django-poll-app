FROM python:3.5

ENV PYTHONUNBUFFERED 1

# Creation of the workdir
RUN mkdir /code
WORKDIR /code
COPY . /copy/

# Add requirements.txt file to container
# COPY requirements.txt /code/

# Install requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Add current directory into container
ADD . /code/
