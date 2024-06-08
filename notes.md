notes.md

https://int10h.org/oldschool-pc-fonts/download/

# how to pair bluetooth device with hid proxy
ref https://github.com/rosmo/go-hidproxy

```bash
sudo raspi-config
# 4. performance options -> enable/disable overlay filesystem

sudo bluetoothctl
discoverable on
pairable on
agent NoInputNoOutput
default-agent
scan on
> Device F7:1A:9C:94:0F:9D ITG wheel remote v2.0
pair F7:1A:9C:94:0F:9D
connect F7:1A:9C:94:0F:9D
trust F7:1A:9C:94:0F:9D
scan off
info F7:1A:9C:94:0F:9D

sudo systemctl reboot
```

note: this doesn't seem to work with this remote
