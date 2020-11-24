# pull official base image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN apt-get update && apt-get install -y \
    --no-install-recommends libpq-dev gcc python3-pip python3-dev setuptools

# copy project
COPY . /app

# copy requirements file
COPY ./requirements/base.in app/requirements/

# Install any needed packages specified in requirements.txt
RUN pip3 install --upgrade pip
RUN pip install --no-cache-dir ipdb
RUN pip install --no-cache-dir -r /requirements.pip
RUN pip3 install --trusted-host pypi.python.org -r requirements/base.in
