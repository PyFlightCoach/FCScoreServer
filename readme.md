A simple Flask API built around the pyflightcoach project to analyse aerobatic flights


To run locally:
```bash
    pip install -r requirements.txt

```



To run in Docker:

```bash
docker build -t fcs_server --build-arg TAG=$(git describe --abbrev=0 --tags ) .
docker run --rm -p 5000:5000 --name=fcs_server fcs_server
```

To add additional clients to the list of known origins add a comma seperated list to the environment
variable EXTRA_CLIENTS:

```bash
docker run --rm -p 5000:5000 --name=fcs_server fcs_server -e CLIENTS="http://localhost:5173,http://localhost:4173,https://pyflightcoach.github.io"
```


```bash
    gunicorn main:app
```