output "vm-master-external-ip" {
  value = data.yandex_compute_instance.vm-master.network_interface.0.nat_ip_address
}
output "vm-master-internal-ip" {
  value = data.yandex_compute_instance.vm-master.network_interface.0.ip_address
}

output "vm-replica-1-external-ip" {
  value = data.yandex_compute_instance.vm-replica-1.network_interface.0.nat_ip_address
}
output "vm-replica-1-internal-ip" {
  value = data.yandex_compute_instance.vm-replica-1.network_interface.0.ip_address
}
