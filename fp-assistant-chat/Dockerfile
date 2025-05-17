# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /application

# Copy the contents of the current directory into the container at /app
COPY application /application

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World
ENV FLASK_APP app.py
ENV PYTHONPATH "${PYTHONPATH}:/application/"

# Run the Flask app when the container launches
CMD ["flask", "run", "--host", "0.0.0.0"]