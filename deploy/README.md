# Odoo BTP – systemd service

## Install (one-time on the VPS)

```bash
sudo cp /home/ubuntu/odoo-projects/btp/deploy/odoo-btp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable odoo-btp   # start on boot (optional)
```

## Usage

```bash
sudo systemctl start odoo-btp
sudo systemctl stop odoo-btp
sudo systemctl restart odoo-btp
sudo systemctl status odoo-btp
```

## Logs

- **journalctl:** `sudo journalctl -u odoo-btp -f`
- **Odoo log file:** `tail -f /home/ubuntu/odoo-projects/btp/odoo19/logs/odoo.log`

## After code changes

```bash
sudo systemctl restart odoo-btp
```
