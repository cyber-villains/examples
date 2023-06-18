FROM python:3.11-slim 

COPY requirements.txt /tmp/requirements.txt
RUN apt-get update && apt-get install && pip install --no-cache-dir -r /tmp/requirements.txt

COPY . .
CMD [ "python", "main.py" ]