output "vm-source-external-ip" {
  value = data.yandex_compute_instance.vm-source.network_interface.0.nat_ip_address
}

output "vm-target-external-ip" {
  value = data.yandex_compute_instance.vm-target.network_interface.0.nat_ip_address
}
