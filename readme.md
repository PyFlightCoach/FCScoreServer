A simple Flask API built around the pyflightcoach project to analyse aerobatic flights

```bash
docker build -t fcs_server --build-arg SOURCE_COMMIT=$(git rev-parse HEAD) .
docker run --rm -p 5000:5000 --name=fcs_server fcs_server
```