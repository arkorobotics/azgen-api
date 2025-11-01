# Start with the base GDAL image
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.11.4

# Set the working directory
WORKDIR /app

# Set up a user to run the app as
RUN useradd -ms /bin/bash azgen  \
    && mkdir /venv \
    && chown azgen /app /venv

# Install any library dependencies
RUN apt-get update \
    && apt-get install -y python3-venv python3-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

USER azgen

# Copy all files from the local project folder into the container
COPY . .

# Install python requirements
RUN python3 -m venv /venv && /venv/bin/pip install -r requirements.txt

# Define which port this will run on
EXPOSE 8082

# Run Production Server
CMD ["/venv/bin/gunicorn","-w" , "4", "-k", "uvicorn.workers.UvicornH11Worker", "azapi.app:app", "--bind", "0.0.0.0:8082"]
