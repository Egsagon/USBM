# USB Monitor

A simple Wireshark based USB bitrate monitor for Windows devices.

### Usage

- Install dependencies: `pip install pyusb numerize`
    - CLI requires `pip install rich`
    - GUI requires `pip install tkinter matplotlib`
- Install [WireShark dependencies](https://www.wireshark.org/download.html) (`TShark` and `USBPcap`)
- Reboot to apply USBPcap driver
- Start `cli.py` or `gui.py`

Note: USBPcap requires to be ran as admin. Privileges will be asked for each interface, unless the script is ran as admin.

### LICENSE

MIT - See the `LICENSE` file

This repo includes `libusb.dll`, licensed LGPL2