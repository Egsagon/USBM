import time
import utils
import subprocess

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
        data = utils.parse_packet(packet)

        with buffer.lock:
            # Create device entry
            buffer.data.setdefault(data['device'], dict(
                name = data['name'],
                interface = interface,
                communications = {}
            ))

            # Create communication entry
            buffer.data[data['device']]['communications'].setdefault(data['direction'], dict(packets = [], speed = 0))

            # Append packet            
            buffer.data[data['device']]['communications'][data['direction']]['packets'].append(dict(
                frame = data['frame'],
                size = data['size']
            ))

def compute(monitor: utils.Monitor) -> None:
    '''
    Put together all raw metrics acquired by capture(), and cleans up internal buffers.
    '''

    # Triple loop, in practice the 1st one and 2rd ones can be ignored because there
    # is no more than 1/2 USBCAP interfaces and multiple comms per port.
    for buffer in monitor.buffers:
        with buffer.lock:
            frame = time.time()

            for device in buffer.data.values():
                for data in device['communications'].values():
                    # Harvest packet sample
                    new_packets = [p for p in data['packets'] if p['frame'] >= frame - utils.FREQUENCY]
                    
                    # Update buffer
                    data['packets'][:] = new_packets
                    data['speed'] = sum(p['size'] for p in new_packets) * 8

def start() -> utils.Monitor:
    '''
    Start monitoring on all interfaces. Returns the capture monitor.
    '''

    monitor = utils.Monitor()
    interfaces = utils.get_interfaces()

    # TODO - Handle multiple interfaces
    # for interface in [interfaces[1]]:
    for interface in interfaces:
        utils.start_thread(capture, interface, monitor.new())
    
    # Start compute thread
    utils.start_thread(utils.looper(compute, monitor))

    return monitor

# EOF