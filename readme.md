A simple Flask API built around the pyflightcoach project to analyse aerobatic flights



```bash
docker build -t fcs_server --build-arg TAG=$(git describe --abbrev=0 --tags ) .
docker run --rm -p 5000:5000 --name=fcs_server fcs_server
```

```bash
    gunicorn main:app
```