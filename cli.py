import time
import monitor
import rich.live
import rich.table

buffer = monitor.start()

def build() -> rich.table.Table:
    '''
    Build the renderable.
    '''

    table = rich.table.Table()
    table.add_column('Address')
    table.add_column('Device')
    table.add_column('Speed')

    for address, data in buffer.data.items():
        speeds = [
            f'{client}: {monitor.utils.numerize(comm['speed'])}bps'
            for client, comm in data['communications'].items()
        ]
        table.add_row(f'{address} @ {data["interface"]["display"]}', data['name'], ', '.join(speeds))
    
    return table

with rich.live.Live(build()) as live:
    try:
        while 1:
            time.sleep(monitor.utils.FREQUENCY)
            live.update(build())
    
    except KeyboardInterrupt:
        pass

# EOF