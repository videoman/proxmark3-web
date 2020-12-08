FROM debian

RUN apt-get update && apt-get -y install --no-install-recommends git libbz2-dev ca-certificates build-essential \
    pkg-config libreadline-dev gcc-arm-none-eabi libnewlib-dev python3-flask python3-flask-sqlalchemy \
    python3-pip python3-dateutil python3-dateparser libev-dev gunicorn3 

RUN pip3 install --upgrade pip && \
    pip3 install datetime && \
    pip3 install Flask-Babel

WORKDIR /home/pi
RUN git clone --depth 1 https://github.com/RfidResearchGroup/proxmark3.git && \
    cd proxmark3 && \
    make all && \
    make install

WORKDIR /home/pi
RUN git clone --depth 1 https://github.com/videoman/proxmark3-web.git
WORKDIR /home/pi/proxmark3-web

CMD gunicorn3 --reload proxmark3-web:app -b:8080
