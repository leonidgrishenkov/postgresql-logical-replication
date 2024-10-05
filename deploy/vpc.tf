# https://terraform-provider.yandexcloud.net/Resources/vpc_network
resource "yandex_vpc_network" "network" {
  name      = "postgresql-vpc"
  folder_id = var.folder_id
}

# https://terraform-provider.yandexcloud.net/Resources/vpc_subnet
resource "yandex_vpc_subnet" "subnet-a" {
  name           = "postgresql-vpc-subnet-a"
  zone           = var.zone
  network_id     = yandex_vpc_network.network.id
  v4_cidr_blocks = ["10.0.0.0/24"]
}
