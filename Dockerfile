# Base (starting) image
FROM python:3.14-slim

# General updates to the operating system
RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install the required Python packages
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
RUN pip3 install gunicorn openpyxl

# Copy the app files (scripts, data, etc.)
COPY ./app.py /code/
RUN mkdir /code/assets
COPY ./assets/ /code/assets

# Other settings
WORKDIR /code/
ENV PYTHONPATH=/code
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000 --workers=2 --threads=4 --worker-class=gthread --forwarded-allow-ips='*' --access-logfile -"

# App start command
CMD ["gunicorn", "app:server"]
