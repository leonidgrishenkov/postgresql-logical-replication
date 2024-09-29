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

You will be prompted to enter information for the certificate. Fill it out as needed.

## Generate Server Certificates

Generate a private key for the server:

```bash
openssl genrsa -out ./certs/server.key 2048
```

Create a certificate signing request (CSR) for the server:

```bash
openssl req -new -key ./certs/server.key -out ./certs/server.csr
```

Again, you will be prompted to enter information. Make sure to set the `Common Name (CN)` to the server's hostname or IP address.

Sign the server certificate with the CA:

```bash
openssl x509 -req -in server.csr -CA ./certs/ca.crt -CAkey ./certs/ca.key -CAcreateserial -out ./certs/server.crt -days 365 -sha256
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
source .env
```

```sh
export IMAGE=cr.yandex/$YC_REGISTRY_ID/postgres-ssl:16.4-bullseye-1.6
```

I will build multi-platform image.
This requires a special builder with `docker-container` driver. If you don't have one, create and activate it:

```sh
docker buildx create --name container-builder --driver docker-container --use --bootstrap
```

Login docker:

```sh
echo $YC_IAM_TOKEN | docker login --username iam --password-stdin cr.yandex
```

Build and push an image to the registry:

```sh
docker build -t $IMAGE \
	--load \
	--platform linux/amd64,linux/arm64 \
	-f ./Dockerfile .
```

```sh
docker push $IMAGE
```

# Create hosts in Yandex Cloud



