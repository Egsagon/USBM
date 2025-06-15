import time
import subprocess
from . import utils

def capture(interface: dict[str], buffer: utils.Buffer) -> None:
    '''
    Constantly captures data from a single interface
    and report to buffer.
    '''

    # Start capture process
    runner = subprocess.Popen(
        (utils.USBCAP, '-d', interface['value']) + utils.USBCAP_OPTS,
        stdout = subprocess.PIPE
    )

    # Start capture parsing process
    parser = subprocess.Popen(
        (utils.TSHARK,) + utils.TSHARK_OPTS,
        stdin = runner.stdout,
        stdout = subprocess.PIPE,
        stderr = subprocess.DEVNULL,
        text = True
    )

    # Process output lines
    for packet in parser.stdout:
        try:
            (port, name), data = utils.parse_packet(packet)

            with buffer.lock:
                buffer.data.setdefault(port, {'packets': [], 'speed': 0})
                buffer.data[port]['name'] = name
                buffer.data[port]['packets'].append(data)
        
        except Exception as err:
            print('Error while processing packet:', repr(err))

def compute(monitor: utils.Monitor) -> None:
    '''
    Put together all raw metrics acquired by capture(), and cleans up internal buffers.
    '''

    for buffer in monitor.buffers:
        with buffer.lock:
            frame = time.time()

            for device in buffer.data.values():
                # Harvest packet sample
                new_packets = [p for p in device['packets'] if p['frame'] >= frame - utils.FREQUENCY]
                
                # Update buffer
                device['packets'][:] = new_packets
                device['speed'] = sum(p['size'] for p in new_packets) * 8

def start() -> utils.Monitor:
    '''
    Start monitoring on all interfaces. Returns the capture monitor.
    '''

    monitor = utils.Monitor()
    interfaces = utils.get_interfaces()

    for interface in interfaces:
        utils.start_thread(capture, interface, monitor.new())
    
    # Start compute thread
    utils.start_thread(utils.looper(compute, monitor))

    return monitor

# EOF