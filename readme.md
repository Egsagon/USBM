# USB Monitor

A simple Wireshark based USB bitrate monitor for Windows devices.

### Usage

- Install dependencies: `pip install pyusb numerize matplotlib`
- Install [WireShark dependencies](https://www.wireshark.org/download.html) (`TShark` and `USBPcap`)
- Reboot to install USBPCap driver
- Start `app.py`

Note: USBPcap requires to be ran as admin. Privileges will be asked for each interface, unless the script is ran as admin.

### LICENSE

MIT - See the `LICENSE` file

This repo includes `libusb.dll`, licensed LGPL2