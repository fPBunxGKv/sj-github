> **⚠️ Warnung**
>
> Ist bei weitem nicht vollständig...

## Installation Ubuntu Server

(aktuell 26.01)
VM basis installation
- 2 CPU
- 4 GB RAM
- 40 GB HD

#### Statische IP setzen

```bash
cd /etc/netplan
sudo vi 50-cloud-init.yaml 
network:
  version: 2
  ethernets:
    ens33:
      addresses:
      - "192.168.175.100/24"
      nameservers:
        addresses:
        - 192.168.175.1
        search: []
      routes:
      - to: "default"
        via: "192.168.175.1"
```
#### IP via DHCP
```bash
cd /etc/netplan
sudo vi 50-cloud-init.yaml 
network:
  version: 2
  ethernets:
    ens33:
      dhcp4: true
```

#### netplan
```bash
netplan try
```

```bash
systemctl status systemd-networkd
```

