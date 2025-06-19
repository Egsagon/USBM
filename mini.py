import time
import monitor
import rich.live
import rich.table

strn = lambda n: monitor.utils.numerize(n) + 'bs'

def render() -> rich.table.Table:
    # Main renderable
    table = rich.table.Table(show_header = False, show_edge = False)

    for port, data in sorted(buffer.data.items()):
        maxes[port] = max(maxes.get(port, 0), data['speed'])
        table.add_row(port.replace('Port ', ''), data['name'], f'{strn(data["speed"])} / {strn(maxes[port])}')
    
    return table

# Start live display
buffer = monitor.start()
maxes: dict[str, float] = {}

with rich.live.Live(get_renderable = render):
    while 1: time.sleep(10)

# EOF