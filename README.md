# Generate SSL Certificates

Using OpenSSL.

```sh
mkdir certs
```

## Create a Certificate Authority (CA)

Generate a private key for the CA:

```bash
openssl genrsa -out ./certs/ca.key 2048
```

Create a self-signed root certificate:

```bash
openssl req -x509 -new -nodes -key ./certs/ca.key -sha256 -days 365 -out ./certs/ca.crt
```

You will be prompted to enter information. You can skip most of the promts, but make sure to set the `Common Name (CN)` to the server's hostname or IP address.

## Generate Server Certificates

Generate a private key for the server:

```bash
openssl genrsa -out ./certs/server.key 2048
```

Create a certificate signing request (CSR) for the server:

```bash
openssl req -new -key ./certs/server.key -out ./certs/server.csr
```

Again, you will be prompted to enter information, make sure you fill the `Common Name (CN)` section.

Sign the server certificate with the CA:

```bash
openssl x509 -req -in ./certs/server.csr -CA ./certs/ca.crt -CAkey ./certs/ca.key -CAcreateserial -out ./certs/server.crt -days 365 -sha256
```

## Generate Client Certificates

Generate a private key for the client:

```bash
openssl genrsa -out ./certs/client.key 2048
```

Create a certificate signing request (CSR) for the client:

```bash
openssl req -new -key ./certs/client.key -out ./certs/client.csr
```

Sign the client certificate with the CA:

```bash
openssl x509 -req -in ./certs/client.csr -CA ./certs/ca.crt -CAkey ./certs/ca.key -CAcreateserial -out ./certs/client.crt -days 365 -sha256
```

Again make sure you fill the `Common Name (CN)` section.

# Build image

```sh
source env.sh
```

I will build multi-platform image to be able to run it on Linux machine.

This requires a special builder with `docker-container` driver. If you don't have one, create and activate it:

```sh
docker buildx create --name container-builder --driver docker-container --use --bootstrap
```

Or if you already have one, just activate it:

```sh
docker buildx use container-builder
```

Login docker:

```sh
echo $YC_IAM_TOKEN | docker login --username iam --password-stdin cr.yandex
```

Build and push an image to the registry:

```sh
docker build -t $POSTGRES_IMAGE \
	--load \
	--platform linux/amd64,linux/arm64 \
	-f ./Dockerfile .
```

```sh
docker push $POSTGRES_IMAGE
```

# Create hosts in Yandex Cloud

Source file with all required environment variables including values for terraform variables (which are start with `TF_VAR_*`):

```sh
source env.sh
```

```sh
cd ./deploy
```

Initialize terraform:

```sh
terraform init
```

Optionally validate configurations:

```sh
terraform validate
```

Create resources:

```sh
terraform apply
```

Show terraform outputs:

```sh
terraform output
```

Set those output values as env variables:

```sh
export VM_SOURCE_EXT_IP=$(terraform output -json | jq -r '.["vm-source-external-ip"].value') \
    && export VM_TARGET_EXT_IP=$(terraform output -json | jq -r '.["vm-target-external-ip"].value')
```

Get serial port output of deployed virtual machines to make sure that everything is correct:

```sh
yc compute instance get-serial-port-output --name postgresql-source
```

# Set logical replication on the source database

Login on the host:

```sh
ssh -i ~/.ssh/dev-hosts yc-user@$VM_SOURCE_EXT_IP
```

Attach to the container:

```sh
docker exec -it postgres /bin/bash
```

## Authentication

In the `/var/lib/postgresql/data/pg_hba.conf` file, enter the hosts to which replication will be performed. In this example, we will use one host that is on the same cloud network.

Open file:

```sh
vim /var/lib/postgresql/data/pg_hba.conf
```

Add the followings configurations:

```sh
hostssl all all target-host-internal-ip/32 md5
hostssl all replication target-host-internal-ip/32 md5
```

You can get internal ip of target host from `terraform output` command.

## WAL log level

Change the logging level for the WAL.

In the `/var/lib/postgresql/data/postgresql.conf` file, find the line with the `wal_level` setting, uncomment it if necessary and set it to `logical`:

```sh
vim /var/lib/postgresql/data/postgresql.conf
```

```sh
wal_level = logical
```

## Apply changes

Restart docker container:

```sh
docker restart postgres
```

Check the container logs:

```sh
docker logs --tail 20 postgres
```

# Add data to the source database

Export repositoty to the host:

```sh
task sync-source
```

Login to the host:

```sh
ssh -i ~/.ssh/dev-hosts yc-user@$VM_SOURCE_EXT_IP
```

Copy sql files into the container:

```sh
docker cp ~/code/postgresql-logical-replication/data/ postgres:/tmp/
```

Start psql session in the container:

```sh
docker exec -it postgres psql "dbname=db user=postgres"
```

Execute DDL query to create schema:

```sh
\i /tmp/data/ddl/users.sql
```

And insert data:

```sh
\i /tmp/data/insert/users.sql
```

# Generate data

```sh
poetry install
```

```sh
export POSTGRES_HOST=$VM_SOURCE_EXT_IP
```

Execute table DDL:

```sh
python src/execute_ddl.py
```

Generate and insert generated data into source database:

```sh
python src/generate_users_data.py --tasks=2 --amount=10000
```
