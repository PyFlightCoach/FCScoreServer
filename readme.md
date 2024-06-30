A simple Flask API built around the pyflightcoach project to analyse aerobatic flights


To run locally:
```bash
    pip install -r requirements.txt
    export CLIENTS="http://localhost:5173,https://pyflightcoach.github.io" 
    gunicorn main:app
```

To run in Docker:

```bash
docker build -t fcs_server --build-arg TAG=$(git describe --abbrev=0 --tags ) .
docker run --rm -p 5000:5000 --name=fcs_server -e CLIENTS="http://localhost:5173,https://pyflightcoach.github.io" fcs_server
```
