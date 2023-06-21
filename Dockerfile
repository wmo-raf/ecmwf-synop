FROM ghcr.io/wmo-im/dim_eccodes_baseimage:latest

ENV TZ="Etc/UTC" \
    DEBIAN_FRONTEND="noninteractive" \
    DEBIAN_PACKAGES="cron bash nano curl git libffi-dev python3-cryptography libssl-dev libudunits2-0 python3-dateparser python3-tz python3-setuptools unzip"

# install dependencies
RUN apt-get update -y && apt-get install -y ${DEBIAN_PACKAGES} \
    && pip3 install --no-cache-dir \
    https://github.com/wmo-im/csv2bufr/archive/refs/tags/v0.6.3.zip \
    https://github.com/wmo-im/bufr2geojson/archive/refs/tags/v0.5.0.zip \
    # cleanup
    && apt autoremove -y  \
    && apt-get -q clean \
    && rm -rf /var/lib/apt/lists/*

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.12.0/wait /wait
RUN chmod +x /wait

# set work directory
WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

ENV PATH="${PATH}:/opt/eccodes/bin"

# copy project
COPY . /usr/src/app/

# add synop.cron to crontab
COPY ./synop.cron /etc/cron.d/synop.cron

RUN chmod 0644 /etc/cron.d/synop.cron && crontab /etc/cron.d/synop.cron


#run docker-entrypoint.sh
ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]