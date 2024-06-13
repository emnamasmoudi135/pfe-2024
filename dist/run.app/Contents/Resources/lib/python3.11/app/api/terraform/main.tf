terraform {
  required_providers {
    proxmox = {
      source = "telmate/proxmox"
      version = ">= 2.7.4"
    }
  }
}

provider "proxmox" {
  pm_api_url          = "https://10.20.0.40:8006/api2/json"
  pm_api_token_id     = "emna@pam!token-id"
  pm_api_token_secret = "dc07a01d-234a-4577-809a-cd7763c9b909"
   pm_tls_insecure = true
      pm_debug = true

}

resource "proxmox_vm_qemu" "testServer" {
  # VM General Settings
  target_node = "proxmox-server"
  vmid        = 166  # L'ID de la nouvelle VM que vous souhaitez créer
  name        = "testemna"

  # VM Advanced General Settings
  onboot = true

  # VM OS Settings
  clone = "WindowsClone"  # VMID of the template to clone

  # VM System Settings
  agent = 1

  # VM CPU Settings
  cores   = 1
  sockets = 1
  cpu     = "host"

  # VM Memory Settings
  memory = 1024

  # VM Network Settings
  network {
    bridge = "vmbr0"
    model  = "virtio"
  }
}