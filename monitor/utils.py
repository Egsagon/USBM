import os
import re
import time
import threading
import subprocess
import collections
import dataclasses

import usb.core
import usb.backend.libusb1

from . import resolver
from numerize.numerize import numerize

FREQUENCY = 1.0

USBCAP = 'C:/Program Files/USBPcap/USBPcapCMD.exe'
TSHARK = 'C:/Program Files/Wireshark/tshark.exe'

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

    New data schematic:
    {
        "DEVICE PORT PATH": {
            "name": "RESOLVED DEVICE NAME"
            "packets": [
                {
                    "frame": "PACKET TIMESTAMP",
                        "size": "PACKET SIZE"
                },
                ...
            ],
            "speed": "TRAFFIC BITRATE"              [ <- injected by monitor.compute() ]
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

def parse_packet(packet: str) -> tuple[tuple[str], dict[str]]:
    '''
    Parses a TSHARK packet.
    Returns the resolved port and packet data.
    '''

    link, frame, size = packet.strip().split('\t')
    address = link.replace('host', '').strip(', ')
    
    return resolver.resolve(address), {
        'frame': float(frame),
        'size': int(size)
    }

def invoke_usbpcap() -> None:
    '''
    Manually open USBPCAP.
    '''

    subprocess.Popen((USBCAP,), start_new_session = True)

# EOF