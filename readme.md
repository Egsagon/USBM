# USB Monitor

A simple Wireshark based USB bitrate monitor for Windows devices.

### Usage

- Install dependencies: `pip install pyusb numerize matplotlib`
- Install [WireShark dependencies](https://www.wireshark.org/download.html) (`TShark` and `USBPcap`)
- Reboot to install USBPCap driver
- Start `app.py`

Note: USBPcap requires to be ran as admin. Privileges will be asked for each interface, unless the script is ran as admin.

### LICENSE

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This repo includes `libusb.dll` (from [the LIBUSB repo](https://github.com/libusb/libusb/releases)), licensed LGPL2.