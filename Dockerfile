FROM python:2.7
LABEL maintainer="fauzi.mkom@gmail.com"
# Set the working directory
WORKDIR /app
# Copy the application code to the container
COPY . /app
# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Specify the command to run on container start
# CMD ["python", "tarik-data.py"]
