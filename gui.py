import random
import monitor
import tkinter
import matplotlib.pyplot
import matplotlib.backends.backend_tkagg

COLORS = [
    '#7986CB', '#33B679', '#8E24AA', '#E67C73', '#F6BF26',
    '#F4511E', '#039BE5', '#3F51B5', '#0B8043', '#D50000'
]

class TkPort(tkinter.LabelFrame):
    '''
    Represents a GUI part containing port info.
    '''

    def __init__(self, parent: object, port: str, data: dict) -> None:
        '''
        Initialize and construct the frame.
        '''

        self.title = f'{port} | {data["name"]}'
        super().__init__(parent, text = self.title, labelanchor = 'n', padx = 10, pady = 10, bg = '#ffffff',
                         font = ('Arial', 12))

        # Yummy GUI code here
        self.plot = []
        self.figure, self.axes = matplotlib.pyplot.subplots(figsize = (4, 0.8), dpi = 100)

        self.axes.set_xticks([])
        self.line, = self.axes.plot([], [], color=random.choice(COLORS), linewidth = 2.3)
        self.figure.subplots_adjust(left = 0.01, right = 0.99, top = 0.99, bottom = 0.01)

        # Style graph
        self.axes.set_ylim(0, 1)
        self.axes.set_xlim(0, 50)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['left'].set_color('#6B6B6B')
        self.axes.spines['bottom'].set_color('#6B6B6B')

        self.axes.tick_params(axis = 'y', labelsize = 8, width = 0, pad = -5, labelcolor = '#6B6B6B')

        for tick in self.axes.yaxis.get_majorticklabels():
            tick.set_horizontalalignment('left')
        
        # Pack graph
        self.canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(self.figure, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill = 'both', expand = True, side = 'top')

    def update_data(self, speed: float) -> None:
        '''
        Update graph.
        '''

        self.config(text=f'{self.title} | {monitor.utils.numerize(speed)}B/s')

        self.plot.append(speed)
        if len(self.plot) > 50:
            self.plot = self.plot[-50:]

        self.line.set_ydata(self.plot)
        self.line.set_xdata(range(len(self.plot)))
        self.axes.set_ylim(0, max(self.plot + [1]) * 1.2)
        self.canvas.draw()

class Scroller(tkinter.Frame):
    '''
    Represents a Tkinter scrollable frame.
    '''

    def __init__(self, master: object) -> None:
        '''
        Initialize the frame.
        '''

        super().__init__(master)

        # Yummy tkinter code
        self.canvas = tkinter.Canvas(self, borderwidth = 0, highlightthickness = 0, bg = '#ffffff')
        self.scrollbar = tkinter.Scrollbar(self, command = self.canvas.yview, bg = '#ffffff')
        self.frame = tkinter.Frame(self.canvas, borderwidth = 0, highlightthickness = 0, relief = 'flat', bg = '#ffffff')
        self.frame.bind('<Configure>', lambda _: self.canvas.configure(scrollregion = self.canvas.bbox('all')))
        self.window = self.canvas.create_window((0, 0), window = self.frame, anchor = 'nw', tags = 'frame')
        self.canvas.config(yscrollcommand = self.scrollbar.set)

        self.canvas.pack(side = 'left', fill = 'both', expand = True)
        self.scrollbar.pack(side = 'right', fill = 'y')
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig('frame', width = e.width))
        self.canvas.bind_all('<MouseWheel>', lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units'))

class App(tkinter.Tk):
    '''
    Represents the app GUI root.
    '''

    def __init__(self) -> None:
        '''
        Initialize the app.
        '''

        super().__init__()
        self.title("USB Monitor")
        self.geometry("600x800")
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.iconphoto(False, tkinter.PhotoImage(file = 'icon.png'))

        self.ports: dict[str, TkPort] = {}
        self.monitor: monitor.utils.Monitor = None

        # Main containers
        self.container = Scroller(self)
        self.container.pack(anchor = 'n', fill = 'both', expand = True)
        tkinter.Frame(self, bg = '#6B6B6B', height = 1).pack(fill = 'x', side = 'top')
        tool_frame = tkinter.Frame(self, padx = 10, pady = 10)
        tool_frame.pack(anchor = 's', fill = 'x')

        # Tools
        tkinter.Button(tool_frame, text = 'Clear', command = self.clear).pack(side = 'left')
        tkinter.Button(tool_frame, text = 'Invoke USBPCAP', command = monitor.utils.invoke_usbpcap).pack(side = 'left')
        tkinter.Button(tool_frame, text = 'Freq -', command = self.set_frequency(-0.05)).pack(side = 'left')
        tkinter.Button(tool_frame, text = 'Freq +', command = self.set_frequency(+0.05)).pack(side = 'left')
        
        self.frequency_label = tkinter.Label(tool_frame)
        self.frequency_label.pack(side = 'right')
        self.set_frequency(0)()
    
    def set_frequency(self, add: float) -> object:
        '''
        Wrapper for frequency changer.
        '''

        def wrapper():
            monitor.utils.FREQUENCY += add
            self.frequency_label.config(text = f'Frequency: {round(monitor.utils.FREQUENCY, 3)}')

        return wrapper
    
    def clear(self) -> None:
        '''
        Clear port discovery.
        '''

        # Clear buffers
        for buffer in self.monitor.buffers:
            with buffer.lock:
                buffer.data.clear()
        
        # Clear frames
        for frame in self.ports.values():
            frame.destroy()
        
        # Clear graph entries
        self.ports.clear()
    
    def start(self):
        '''
        Start the app.
        '''

        self.monitor = monitor.start()

        # Use after() inside a thread loop to stay inside tk loop
        monitor.utils.start_thread(monitor.utils.looper(self.after, 0, self.updater))
        self.mainloop()
    
    def updater(self) -> None:
        '''
        Looped method that actualizes the app.
        '''

        for port, data in self.monitor.data.items():

            # Create new frame
            if port not in self.ports:
                frame = TkPort(self.container.frame, port, data)
                frame.pack(fill = 'x', padx = 10, pady = 10)
                self.ports[port] = frame
            
            # Append speed report
            self.ports[port].update_data(data['speed'])

    def close(self) -> None:
        '''
        Kill all threads.
        '''

        self.destroy()
        exit()

if __name__ == '__main__':
    App().start()

# EOF