import os
import re
import time
import functools
import threading
import subprocess
import collections
import dataclasses

import usb.core
import usb.util
import usb.backend.libusb1

from numerize.numerize import numerize

FREQUENCY = 1.0

USBCAP = 'C:/Program Files/USBPcap/USBPcapCMD.exe'
TSHARK = 'C:/Program Files/Wireshark/tshark.exe'

USBDLL = os.path.abspath('libusb.dll')
USBLIB = usb.backend.libusb1.get_backend(find_library = lambda _: USBDLL)

USBCAP_OPTS = ('-o', '-', '-A')
TSHARK_OPTS = ('-i', '-', '-l', '-n', '-Y', 'usb', '-T', 'fields',
               '-e', 'usb.addr', '-e', 'frame.time_epoch', '-e', 'usb.data_len')

@dataclasses.dataclass
class Buffer:
    '''
    Data buffer bundled with a lock.
    '''

    data: dict = dataclasses.field(default_factory = dict)
    lock: threading.Lock = dataclasses.field(repr = False, default_factory = threading.Lock)

@dataclasses.dataclass
class Monitor:
    '''
    Supervising instance that can create Buffer objects on demand.
    The object itself is a chained buffer of all buffers (optimized, pfew).

    Data schematic:
    {
        "DEVICE ADDRESS": {
            "name": "DEVICE NAME",
            "interface": {
                "display": "INTERFACE NAME",
                "value": "INTERFACE PATH"
            },
            "communications": {
                "PACKET DIRECTION OR in/out IF TO HOST": {
                    "packets": [
                        "frame": "PACKET TIMESTAMP",
                        "size": "PACKET SIZE"
                    ],
                    "speed": "TRAFFIC BIRATE"       [ <- injected by monitor.compute() ]
                }
            }
        }
    }
    '''

    buffers: list[Buffer] = dataclasses.field(repr = False, default_factory = list)
    data: collections.ChainMap = dataclasses.field(default_factory = collections.ChainMap)

    def new(self) -> Buffer:
        '''
        Create a new child buffer.
        '''

        buffer = Buffer()
        self.buffers.append(buffer)
        self.data = self.data.new_child(buffer.data)
        return buffer

@functools.cache
def get_device_name(address: str) -> str:
    '''
    Get a device name from its address.
    Utilizes USBLIB via PYUSB when not cached.
    '''

    bus, address, *_ = address.split('.')

    for dev in usb.core.find(find_all = True, backend = USBLIB):

        if str(dev.bus) == bus and str(dev.address) == address:

            try:
                manufacturer = usb.util.get_string(dev, dev.iManufacturer)
                product = usb.util.get_string(dev, dev.iProduct)
                name = f'[{manufacturer.strip()}] {product.strip()}'
            
            except NotImplementedError:
                name = 'Weird USB device'

            return f'#{dev.idVendor}:{dev.idProduct} {name}'

    return 'USB device'

def get_interfaces() -> list[dict[str]]:
    '''
    Get all running USBPCAP interfaces.
    '''

    raw = subprocess.run((USBCAP, '--extcap-interfaces'), text=True, capture_output=True)
    return [dict(re.findall(r'\{(.*?)=(.*?)\}', i)) for i in raw.stdout.strip().split('\n')]

def start_thread(callable: object, *args, **kwargs) -> threading.Thread:
    '''
    Starts a thread in daemon mode.
    '''

    thread = threading.Thread(target = callable, args = args, kwargs = kwargs, daemon = True)
    thread.start()

    return thread

def looper(callable: object, *args, **kwargs) -> object:
    '''
    Wraps looping a callable.
    Frequency does not account for execution time.
    '''

    def wrapper() -> None:
        while 1:
            callable(*args, **kwargs)
            time.sleep(FREQUENCY)
    
    return wrapper

def parse_packet(packet: str) -> dict[str]:
    '''
    Parses a TSHARK packet.
    '''

    link, frame, size = packet.strip().split('\t')
    parts = device, direction = link.split(',')

    # For direct communications with host, set direction depending on position on host
    # in the parts (99% of packets). This allows 2 way USB coms representation, avoids
    # having an abstract "host" device and does not confuse USBLIB resolver.
    if 'host' in link:
        device = sorted(parts)[0]
        direction = ('in', 'out')[direction == 'host']
    
    return dict(
        device = device,
        name = get_device_name(device),
        direction = direction,
        frame = float(frame),
        size = int(size)
    )

def invoke_usbpcap() -> None:
    '''
    Manually open USBPCAP.
    '''

    subprocess.Popen((USBCAP,), start_new_session = True)

# EOF