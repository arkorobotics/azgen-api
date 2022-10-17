# Start with the universal Python 3.9 image
FROM osgeo/gdal:ubuntu-small-3.5.2

# Install any library dependencies
RUN apt-get update && apt-get install -y python3-pip && rm -rf /var/lib/apt/lists/*

# Copy all files from the local project folder into the container
COPY . .

# Install python requirements
RUN pip install -r requirements.txt

# Define which port this will run on
EXPOSE 8082

# Run Production Server
CMD ["gunicorn","-w" , "4", "-k", "uvicorn.workers.UvicornH11Worker", "azapi.app:app", "--bind", "0.0.0.0:8082"]
