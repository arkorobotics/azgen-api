# AZGen API
To test the API:

Within a virtualenv, run as a wsgi app.

For example, using `uvicorn`:
```shell
(venv)> cd ./api
(venv)> pip install uvicorn
(venv)> pip install fastapi
(venv)> uvicorn azapi:app --reload --port 8080
// site is now accessible on localhost:8080
```

Test using `httpie`:
```shell
(venv)> cd ./api
(venv)> pip install httpie
(venv)> http http://localhost:8000
// Get a string return :)
(venv)> http POST http://localhost:8000 < sample.json
```

## Docker

Command to build image:
```
docker build -t azgen-api:latest .
```

Command to run image:
```
docker run -it --rm -p 8082:8082 azgen-api:latest
```

### Credits

API back end by @thedeltaflyer; Activation zone generation by @arkorobotics;