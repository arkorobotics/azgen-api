# AZGen API

# Development

To test the API:

Within a virtualenv, run as a wsgi app.

For example, using the built-in `uvicorn` server:

```shell
(venv)> pip install -e ".[test]"
(venv)> azgen --port 8080 --debug
# site is now accessible on localhost:8080
```

If you are unable to get it running locally due to OSGEO/GDAL issues, you can run it from within a docker container:

```shell
# Run the osgeo/gdal image
> docker run docker run --rm -it -p 8082:8082 -v /path/to/azgen-api/:/app/ osgeo/gdal:ubuntu-small-3.5.2 bash
# cd to the app directory
root@docker_image:/# cd /app
# Install/Update missing dependencies
root@docker_image:/app# apt-get update && apt-get install -y python3-pip git
# Install the local repo
root@docker_image:/app# pip install -e ".[test]"
# Run the app as needed for development
root@docker_image:/app# azgen -h
usage: azgen [-h] [-b BIND] [-p PORT] [--debug] [-v]

Azgen API CLI. This starts a dev server for the API.

optional arguments:
  -h, --help            show this help message and exit
  -b BIND, --bind BIND  Host to Bind to. Default: 127.0.0.1
  -p PORT, --port PORT  Port to run the API on. Default: 8082
  --debug               Print debug messages.
  -v, --version         Print version and exit.
```

Test using `httpie`:

```shell
(venv)> pip install httpie
(venv)> http http://localhost:8080
# Get a string return :)
(venv)> http POST http://localhost:8000 < sample.json
```

# To Build/Run

## Docker

Command to build image:

```
docker build -t azgen-api:latest .
```

Command to run image:

```
docker run -it --rm -p 8082:8082 azgen-api:latest
```

# Credits

API backend created with the assistance of @thedeltaflyer; Activation zone generation by @arkorobotics;