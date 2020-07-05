import tkinter as tk
from tkinter import ttk
from pyautocad import Autocad, APoint, ACAD
import array, math, re

''' Main Application '''

class main_app:
    window = tk.Tk()
    window.geometry('600x400')
    window.title('Property Lines Drafter v0.1')

    def __init__(self):
        self.property_lines_frame = property_lines_frame(self.window)
        self.confirm_buttons_frame = confirm_buttons_frame(self.window)

        self.window.grid_rowconfigure(0, weight = 1)
        self.window.grid_columnconfigure(0, weight = 1)

        self.window.mainloop()

    @classmethod
    def quit(cls):
        cls.window.destroy()

class property_lines_frame:
    def __init__(self, host):
        self.host = host

        self.frame = tk.Frame(self.host, bd = 2, relief = tk.GROOVE)
        self.frame.grid(row = 0, column = 0, sticky = tk.NSEW, padx = 10, pady = (10, 0))

        self.title = tk.Label(self.frame, text = 'Property Lines')
        self.title.pack(anchor = tk.NW)

        self.deed_data_frame = deed_data(self.frame)

class deed_data:

    lines = list()

    def __init__(self, host):
        self.host = host

        self.border = tk.Frame(self.host, bd = 2, relief = tk.SUNKEN)
        self.border.pack(side = tk.TOP, fill = tk.BOTH, expand = True, padx = 10, pady = (5, 0))

        self.canvas = tk.Canvas(self.border, highlightthickness = 0)
        self.canvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)

        self.frame = tk.Frame(self.canvas)
        self.canvasFrame = self.canvas.create_window((0,0), window = self.frame, anchor = tk.NW)

        self.scrollbar = tk.Scrollbar(self.canvas, orient = 'vertical', command = self.canvas.yview)
        self.scrollbar.pack(side = tk.RIGHT, fill = tk.Y)

        self.canvas.config(yscrollcommand = self.scrollbar.set)

        self.frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.frame_width)

        self.column_headers = [
            (column_header(self.frame, column = 0, text = 'Line')),
            (column_header(self.frame, column = 1, text = 'Distance')),
            (column_header(self.frame, column = 2, text = 'N/S')),
            (column_header(self.frame, column = 3, text = 'Bearing')),
            (column_header(self.frame, column = 4, text = 'E/W')),
            ]

        self.frame.grid_columnconfigure([1, 3], weight = 1)

        for i in range(1, 4):
            deed_data.lines.append(deed_row(self.frame, i))

        self.line_settings_frame = tk.Frame(self.host, bd = 10)
        self.line_settings_frame.pack(side = tk.BOTTOM, fill = tk.X)

        self.insert = button(self.line_settings_frame, text = 'Insert', width = 12, side = tk.LEFT, command = self.insert_row)
        self.delete = button(self.line_settings_frame, text = 'Delete', width = 12, side = tk.LEFT, command = self.delete_row, padx = 10)
        self.close = button(self.line_settings_frame, text = 'Add Line to Close', width = 20, side = tk.LEFT, command = self.close_line) 

    def frame_width(self, event):
        canvas_width = event.width - 19
        self.canvas.itemconfig(self.canvasFrame, width = canvas_width)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion = self.canvas.bbox('all'))

    def insert_row(self):
        self.lines.insert(len(self.lines), deed_row(self.frame, (len(self.lines) + 1)))

    def delete_row(self):
        if len(self.lines) > 3:
            self.lines[-1].line_no.label.destroy()
            self.lines[-1].line_distance.distance.destroy()
            self.lines[-1].line_NS.combobox.destroy()
            self.lines[-1].line_bearing.bearing.destroy()
            self.lines[-1].line_EW.combobox.destroy()
            del self.lines[-1]

    def close_line(self):
        property.get_values()

        if is_closed() == False:

            last_line = property.lines[-1]
            second_last_vertex = property.vertex[-2]
            last_vertex = property.vertex[-1]
            first_vertex = property.vertex[0]

            closing_angle = DecDeg_to_DMS(
                get_closing_angle(
                    APoint.distance_to(first_vertex.coordinates, second_last_vertex.coordinates),
                    APoint.distance_to(last_vertex.coordinates, first_vertex.coordinates),
                    APoint.distance_to(last_vertex.coordinates, second_last_vertex.coordinates),
                    last_line.angle
                    )
                )

            self.insert_row()
            self.lines[-1].line_distance.distance_text.set(
                round(APoint.distance_to(
                    last_vertex.coordinates, 
                    first_vertex.coordinates), 3)
                )
            self.lines[-1].line_NS.combobox.set(closing_angle[0])
            self.lines[-1].line_bearing.bearing_text.set(closing_angle[1])
            self.lines[-1].line_EW.combobox.set(closing_angle[2])


class deed_row:
    def __init__(self, host, i):
        self.host = host

        self.line_no = row_header(self.host, row = i, text = i)
        self.line_distance = distance_entry(self.host, row = i, column = 1, padx = 3)
        self.line_NS = combo_box(self.host, row = i, column = 2, values = ['N', 'S'], width = 5)
        self.line_bearing = bearing_entry(self.host, row = i, column = 3, padx = 3)
        self.line_EW = combo_box(self.host, row = i, column = 4, values = ['E', 'W'], width = 5, padx = (0, 1))


class confirm_buttons_frame:
    def __init__(self, host):
        self.host = host

        self.frame = tk.Frame(self.host)
        self.frame.grid(row = 1, column = 0, sticky = tk.NSEW, padx = 10, pady = 10)

        self.cancel = button(self.frame, text = 'Cancel', width = 12, side = tk.RIGHT, command = main_app.quit)
        self.OK = button(self.frame, text = 'OK', width = 12, side = tk.RIGHT, padx = 10, command = draw)

''' Styles '''

style = ttk.Style()
style.configure('TCombobox', padding = 1)

class column_header:
    def __init__(self, host, column, text):
        self.host = host

        self.label = tk.Label(self.host, text = text)
        self.label.grid(row = 0, column = column, sticky = tk.EW)

class row_header:
    def __init__(self, host, row, text):
        self.host = host

        self.label = tk.Label(self.host, text = text)
        self.label.grid(row = row, column = 0, sticky = tk.EW)

class distance_entry:
    def __init__(self, host, row, column, padx, pady = None):
        self.host = host

        self.distance_text = tk.StringVar(self.host, '0.0')
        self.distance = tk.Entry(self.host, bd = 1, relief = tk.SOLID, textvariable = self.distance_text)
        self.distance.grid(row = row, column = column, sticky = tk.EW, padx = padx, pady = pady)

class bearing_entry:
    def __init__(self, host, row, column, padx):
        self.host = host
        
        self.bearing_text = tk.StringVar(self.host, r'''0º 0' 0"''')
        self.bearing = tk.Entry(host, bd = 1, relief = tk.SOLID, textvariable = self.bearing_text)
        self.bearing.grid(row = row, column = column, sticky = tk.EW, padx = padx)

class combo_box:
    def __init__(self, host, row, column, values = None, width = None, padx = None, postcommand = None, textvariable = None):
        self.host = host
        
        self.combobox = ttk.Combobox(self.host, style = 'TCombobox', values = values, width = width, state = 'readonly', postcommand = postcommand, textvariable = textvariable)
        self.combobox.grid(row = row, column = column, padx = padx, sticky = tk.EW)

class button:
    def __init__(self, host, text, width, side, padx = None, command = None):
        self.host = host
        
        self.button = tk.Button(self.host, text = text, width = width, relief = tk.SOLID, bd = 1, bg = '#e5e5e5', command = command)
        self.button.pack(side = side, padx = padx)

''' AutoCAD classes'''

class line:
    def __init__(self, distance, angle):
        self.distance = distance
        self.angle = angle

class vertex:
    def __init__(self, coordinates, interior_angle = None):
        self.coordinates = coordinates
        self.interior_angle = interior_angle

''' Formulas'''

def positive_angle(angle):
    if angle < 0:
        angle += 360

    elif angle >= 360:
        angle -= 360

    return angle

def get_coordinates(distance, angle):
    return APoint(
        (math.cos(math.radians(angle))*distance),
        (math.sin(math.radians(angle))*distance)
        )

def get_interior_angle(current_angle, prev_angle):
    if property.clockwise == True:
        return positive_angle(180 + current_angle - prev_angle)
    else:
        return positive_angle(180 - current_angle + prev_angle)

def get_closing_angle(a, b, c, prev_angle):
    A = SSS(a, b, c)

    if property.clockwise == True:
        return positive_angle(prev_angle - 180 + A)

    else:
        return positive_angle(prev_angle - 180 - A)

def is_clockwise(origin, angle, next_vertex, prev_vertex):
    if 90 > angle >= 0 and (next_vertex.x > origin.x and prev_vertex.y < origin.y):
        return True

    elif 180 > angle >= 90 and (next_vertex.y > origin.y and prev_vertex.x > origin.x):
        return True

    elif 270 > angle >= 180 and (next_vertex.x < origin.x and prev_vertex.y > origin.y):
        return True

    elif 360 > angle >= 270 and (next_vertex.y < origin.y and prev_vertex.x < origin.x):
        return True

    else:
        return False

def SSS(a, b, c):
    return math.degrees(math.acos((b**2 + c**2 - a**2) / (2*b*c)))

def DMS_to_DecDeg(NS, bearing, EW):
    DMS = dict()
    DMS.setdefault('degrees', 0)
    DMS.setdefault('minutes', 0)
    DMS.setdefault('seconds', 0)

    pattern = re.compile(r'\d*\.\d+|\d+')
    matches = pattern.findall(bearing)

    try:
        DMS['degrees'] = float(matches[0])
        DMS['minutes'] = float(matches[1])
        DMS['seconds'] = float(matches[2])

    except Exception:
        pass

    dd = DMS['degrees'] + (DMS['minutes'] / 60) + (DMS['seconds'] / 3600)

    if NS == 'N' and EW == 'E':
        return 90 - dd

    if NS == 'N' and EW == 'W':
        return 90 + dd

    if NS == 'S' and EW == 'E':
        return 270 + dd

    if NS == 'S' and EW == 'W':
        return 270 - dd

def DecDeg_to_DMS(angle):
    dd = round(angle, 4)

    if 90 > angle >= 0:
        dd = dd
        bearing = angle_to_bearing(dd)

        NS = 'N'
        EW = 'E'
        return NS, bearing, EW

    elif 180 > angle >= 90:
        dd = dd - 90
        bearing = angle_to_bearing(dd)

        NS = 'N'
        EW = 'W'
        return NS, bearing, EW

    elif 270 > angle >= 180:
        dd = 270 - dd
        bearing = angle_to_bearing(dd)

        NS = 'S'
        EW = 'W'
        return NS, bearing, EW

    elif 360 > angle >= 270:
        dd = dd - 270
        bearing = angle_to_bearing(dd)

        NS = 'S'
        EW = 'E'
        return NS, bearing, EW

def angle_to_bearing(angle):
    degrees = int(angle)
    minutes = int(((angle - degrees) *60))
    seconds = int(((((angle - degrees) * 60) - minutes) * 60))
    bearing = f'''{str(degrees)}º {str(minutes)}' {str(seconds)}"'''

    return bearing

def is_closed():
    if (round(property.vertex[-1].coordinates.x) == 0 and 
            round(property.vertex[-1].coordinates.y) == 0):
        return True

    else:
        return False

''' Plotter '''

class property:
    lines = list()
    array = list()
    vertex = list()

    @classmethod
    def get_values(cls):
        cls.lines.clear()
        cls.array.clear()

        cls.num_of_lines = len(getattr(deed_data, 'lines'))

        for i in range(cls.num_of_lines):
            cls.lines.append(
                line(
                    float(deed_data.lines[i].line_distance.distance.get()),
                    DMS_to_DecDeg(
                        deed_data.lines[i].line_NS.combobox.get(),
                        deed_data.lines[i].line_bearing.bearing.get(),
                        deed_data.lines[i].line_EW.combobox.get()
                        )
                    )
                )

        cls.vertex.append(vertex(APoint(0, 0, 0)))

        for i in range(cls.num_of_lines):
            cls.vertex.append(
                vertex(
                    get_coordinates(
                        cls.lines[i].distance,
                        cls.lines[i].angle
                        ) + 
                    cls.vertex[i].coordinates
                    )
                )

        cls.clockwise = is_clockwise(
            cls.vertex[0].coordinates,
            cls.lines[0].angle,
            cls.vertex[1].coordinates,
            cls.vertex[-2].coordinates
            )

        for i in range(cls.num_of_lines):
            cls.vertex[i].interior_angle = float(
                get_interior_angle(
                    cls.lines[i].angle,
                    cls.lines[i-1].angle
                    )
                )

        if is_closed() == False:
            for i in range(cls.num_of_lines + 1):
                cls.array += list(cls.vertex[i].coordinates)

        else:
            for i in range(cls.num_of_lines):
                cls.array += list(cls.vertex[i].coordinates)
            cls.array += list(cls.vertex[0].coordinates)

def draw():
    acad = Autocad(create_if_not_exists = False)
    property.get_values()
    polyline = acad.model.AddPolyline(array.array('d', property.array))
    acad.prompt('Drawing successful!')

main_app()

# TODO: Errors @ status bar