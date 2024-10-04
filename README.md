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

## Generate Server Certificates

Generate a private key for the server:

```bash
openssl genrsa -out ./certs/server.key 2048
```

Create a certificate signing request (CSR) for the server:

```bash
openssl req -new -key ./certs/server.key -out ./certs/server.csr
```

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
	-f ./docker/postgresql/Dockerfile
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
export VM_MASTER_EXT_IP=$(terraform output -json | jq -r '.["vm-master-external-ip"].value') \
    && export VM_REPLICA_1_EXT_IP=$(terraform output -json | jq -r '.["vm-replica-1-external-ip"].value')
```

Get serial port output of deployed virtual machines to make sure that everything is correct:

```sh
yc compute instance get-serial-port-output --name postgresql-source
```

# Set logical replication on the master database

Login on the host:

```sh
ssh -i ~/.ssh/dev-hosts yc-user@$VM_MASTER_EXT_IP
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
hostssl all all 10.0.0.32/32 md5
hostssl all replication 10.0.0.32 md5
```

Where `10.0.0.32` - internal IP of the target host with a subnet mask, that we can get from `terraform output` command.

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

# Generate data

```sh
poetry env use (which python3)
```

```sh
poetry install
```

```sh
poetry shell
```

```sh
export POSTGRES_HOST=$VM_MASTER_EXT_IP
```

Execute table DDL:

```sh
python src/execute_ddl.py
```

Generate and insert generated data into master database:

```sh
python src/generate_users_data.py --tasks=4 --amount=100000
```

# Create schema in the replica

Login on the replica host.

```sh
ssh -i ~/.ssh/dev-hosts yc-user@$VM_REPLICA_1_EXT_IP
```

Execute `pg_dump` command to dump schema of source database.

```sh
pg_dump -h 10.0.0.8 \
    -U postgres \
    -p 15432 \
    --schema-only \
    --no-privileges \
    --no-subscriptions \
    -d db -Fd -f /tmp/db_dump
```

You will be prompt to enter a password.

Restore this schema:

```sh
pg_restore -Fd -v \
    --single-transaction \
    -s --no-privileges \
    -h localhost \
    -U postgres \
    -p 5432 \
    -d db /tmp/db_dump
```

# Create publication and subscription

In the master database create publication:

```sql
CREATE PUBLICATION migration FOR ALL TABLES;
```

In the replica create subscription:

```sql
CREATE SUBSCRIPTION migration
CONNECTION 'host=10.0.0.8 port=15432 user=postgres password= sslmode=require dbname=db'
PUBLICATION migration;
```

Where:

-   `host=10.0.0.8` - internal IP of the source host, that we can get from `terraform output` command as well.
-   `port=15432` - exposed docker port

# Replication status

Replication statistics on the source host:

```sql
SELECT * FROM pg_stat_replication;
```

On the target host:

```sql
SELECT * FROM pg_stat_subscription;
```

```sql
SELECT * FROM pg_subscription;
```

```sql
SELECT * FROM pg_publication;
```

```sql
SELECT * FROM pg_replication_slots;
```
