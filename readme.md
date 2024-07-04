A simple Flask API built around the pyflightcoach project to analyse aerobatic flights


To run locally:
```bash
    pip install -r requirements.txt
    gunicorn main:app
```

To run in Docker:

```bash
    docker build -t fcs_server --build-arg TAG=$(git describe --abbrev=0 --tags ) .
    docker run --rm -p 5000:5000 --name=fcs_server fcs_server
```

To allow different clients:

```bash
    docker run --rm -p 5000:5000 --name=fcs_server -e CLIENTS="http://client1,http://client2" fcs_server
```

To run and connect to a unix socket:

```bash
    docker run --rm -e "SOCKET_OVERRIDE=unix:<YOURPATH/YOURSOCKET.sock>" -v <YOURPATH>:<YOURPATH> --name=fcs_server fcs_server
```
