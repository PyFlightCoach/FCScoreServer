A simple Flask API built around the pyflightcoach project to analyse aerobatic flights

docker build -t fcs_server .

docker run --rm -p 5000:5000 --name=fcs_server fcs_server