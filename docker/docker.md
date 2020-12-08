# Docker

proxmark3-web can be run inside Docker for ease of use, it should work on any Docker host, including a Raspberry Pi.

## Building

From the directory with the Dockerfile, run:

```sh
$ docker build -t proxmark3-web .
```

This will create a new Docker container with the latest Proxmark3 code as well as this proxmark3-web repository

## Running

```sh
docker run -it --rm --name proxmark \
    -p 8080:8080 \
    --device=/dev/ttyACM0 \
    proxmark
```

Be sure to pass the Proxmark device to the container, it should be `/dev/ttyACM0` on most Linux systems.

