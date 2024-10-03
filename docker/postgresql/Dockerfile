FROM postgres:16.4-bullseye

# Copy SSL certificates
COPY ./certs/server.crt /var/lib/postgresql/certs/server.crt
COPY ./certs/server.key /var/lib/postgresql/certs/server.key
COPY ./certs/ca.crt /var/lib/postgresql/certs/ca.crt

RUN apt update \
    && apt upgrade -y \
    && apt install -y --no-install-recommends curl vim \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# Set permissions
RUN chown postgres:postgres /var/lib/postgresql/certs/server.crt /var/lib/postgresql/certs/server.key && \
    chmod 600 /var/lib/postgresql/certs/server.key
