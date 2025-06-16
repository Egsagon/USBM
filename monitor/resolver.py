import os
import functools
import usb.core
import usb.util
import usb.backend.libusb1

USBDLL = os.path.abspath('monitor/libusb.dll')
USBLIB = usb.backend.libusb1.get_backend(find_library = lambda _: USBDLL)

def get_path(device: usb.core.Device, _r: str = '') -> str:
    '''
    Retrieve the physical port path of a device recursively.
    '''

    if device.port_number != 0:
        _r = str(device.port_number) + ' > ' + _r

    if device.parent is None: return _r[:-3]
    return get_path(device.parent, _r = _r)

def get_name(device: usb.core.Device) -> str:
    '''
    Retrieve a device pretty name. Falls back to device ID.
    '''

    try:
        manufacturer = usb.util.get_string(device, device.iManufacturer)
        product = usb.util.get_string(device, device.iProduct)
        return f'[{manufacturer.strip()}] {product.strip()}'
    
    except NotImplementedError:
        return f'Device #{device.idVendor}:{device.idProduct}'

@functools.cache
def resolve(id: str) -> tuple[str, str]:
    '''
    Get a unique port path representation and it's associated name.
    '''

    bus, address, *_ = id.split('.')
    name = 'Unknown device'

    for device in usb.core.find(True, USBLIB):
        if str(device.bus) == bus and str(device.address) == address:

            path = get_path(device) or '0' # Fallback to root hub
            name = get_name(device)

            if path is None: break # Ensures fallback
            return 'Port ' + path, name
    
    return f'Device {id} (unknown port)', name

# EOF