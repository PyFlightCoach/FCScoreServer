A simple Flask API built around the pyflightcoach project to analyse aerobatic flights



```bash
docker build -t fcs_server --build-arg TAG=$(git describe --abbrev=0 --tags ) .
docker run --rm -p 8000:8000 --name=fcs_server fcs_server
```

```bash
    gunicorn main:app --workers 10 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 600
```