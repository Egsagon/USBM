import time
import monitor

import rich
import rich.box
import rich.live
import rich.table

def plot(data: list[float], size: tuple = (1, 0), style: str = 'bold') -> str:
    # Console plotting utility.

    blocks = ' ▁▂▃▄▅▆▇█'

    vmax = max(data)
    vmax = vmax if vmax != 0 else 1e-9

    block_levels = len(blocks) - 1
    total_levels = size[0] * block_levels

    graph = []
    normalized = [int(point / vmax * total_levels) for point in data]

    # Adjust graph size
    diff = size[1] - len(data)
    if size[1] and diff > 0: normalized += [0] * diff
    if size[1] and diff < 0: normalized = normalized[-diff:]
    
    for line in reversed(range(size[0])):
        raw = ''
        for level in normalized:
            block_index = level - line * block_levels
            if block_index <= 0: raw += ' '
            elif block_index >= block_levels: raw += blocks[-1]
            else: raw += blocks[block_index]
        
        graph.append(f'[{style}]{raw}[/{style}]')

    return '\n'.join(graph)

def bake(value: float) -> str:
    # bake a float

    return monitor.utils.numerize(value) + 'bs'

def render() -> rich.table.Table:
    # Main renderable

    table = rich.table.Table(
        rich.table.Column('Location', max_width = 15),
        rich.table.Column('Device', max_width = 35),
        rich.table.Column('Traffic', overflow = 'ignore'),
        box = rich.box.Box('  ╷ \n  │ \n╶─┼╴\n  │ \n  │ \n╶─┼╴\n  │ \n  ╵ \n'),
        expand = True,
        show_lines = True
    )

    for port, data in sorted(buffer.data.items()):
        # Update plot points
        if not port in points: points[port] = [0, []]
        points[port][1].append(data['speed'])
        points[port][0] = max([points[port][0]] + points[port][1])
        if len(points[port][1]) > 50: points[port][1] = points[port][1][-50:]
        
        # Make graph
        top, bottom = plot(points[port][1], size = (2, 30), style = 'blue on black').split('\n')
        table.add_row(
            port,
            data['name'],
            f'{top} [dim]=[/dim] {bake(data["speed"])}\n{bottom}'
            f'[dim]+[/dim] {bake(points[port][0])}'
        )
    
    return table

# Start live display
buffer = monitor.start()
points: dict[str, list[float, list[float]]] = {}

with rich.live.Live(get_renderable = render):
    while 1: time.sleep(10)

# EOF