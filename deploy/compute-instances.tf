locals {
  username     = "yc-user"
  ssh_key_path = "~/.ssh/dev-hosts.pub"
}

resource "yandex_compute_instance" "vm-master" {
  name        = "postgresql-master"
  hostname    = "postgresql-master"
  platform_id = "standard-v3"
  zone        = var.zone
  folder_id   = var.folder_id

  resources {
    cores         = 2
    memory        = 2
    core_fraction = 100
  }

  boot_disk {
    initialize_params {
      image_id = var.image_id
      type     = "network-hdd"
      size     = 20
    }
    auto_delete = true
  }

  network_interface {
    subnet_id          = yandex_vpc_subnet.subnet-a.id
    security_group_ids = [yandex_vpc_security_group.sg.id]
    nat                = true
    ipv4               = true
  }

  metadata = {
    user-data = templatefile("./cloud-init.yaml",
      {
        ssh_key_path      = file("${local.ssh_key_path}"),
        username          = local.username,
        iam_token         = var.iam_token
        postgres_image    = var.postgres_image,
        postgres_user     = var.postgres_user,
        postgres_password = var.postgres_password,
        postgres_db       = var.postgres_db,
        postgres_port     = var.postgres_port,
    })
  }
}

data "yandex_compute_instance" "vm-master" {
  instance_id = yandex_compute_instance.vm-master.id
}

resource "yandex_compute_instance" "vm-replica-1" {
  name        = "postgresql-replica-1"
  hostname    = "postgresql-replica-1"
  platform_id = "standard-v3"
  zone        = var.zone
  folder_id   = var.folder_id

  resources {
    cores         = 2
    memory        = 2
    core_fraction = 100
  }

  boot_disk {
    initialize_params {
      image_id = var.image_id
      type     = "network-hdd"
      size     = 20
    }
    auto_delete = true
  }

  network_interface {
    subnet_id          = yandex_vpc_subnet.subnet-a.id
    security_group_ids = [yandex_vpc_security_group.sg.id]
    nat                = true
    ipv4               = true
  }

  metadata = {
    user-data = templatefile("./cloud-init.yaml",
      {
        ssh_key_path      = file("${local.ssh_key_path}"),
        username          = local.username,
        iam_token         = var.iam_token
        postgres_image    = var.postgres_image,
        postgres_user     = var.postgres_user,
        postgres_password = var.postgres_password,
        postgres_db       = var.postgres_db,
        postgres_port     = var.postgres_port,
    })
  }
}


data "yandex_compute_instance" "vm-replica-1" {
  instance_id = yandex_compute_instance.vm-replica-1.id
}
