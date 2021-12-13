import ctypes
import sys
import time
import numpy as np

#path_to_dll = r'C:\Users\sergeyg\WORK.FILES\Bruker Nano APIs\Device API\Sample\Bruker.API.Devices64.dll'
path_to_dll = r'C:\Users\sergeyg\Github\Bruker Nano APIs\Device API\Sample\Bruker.API.Devices64.dll'

# Type describes one line segment in image for scanning.
class TSegment(ctypes.Structure):
    # _pack_ = 1
    _fields_ = [
        ('Y', ctypes.c_uint8),
        ('XStart', ctypes.c_uint8),
        ('XEnd', ctypes.c_uint8)
    ]


# Specifies a position inside image. Type is used to set or get a beam position.
class TPoint(ctypes.Structure):
    # _pack_ = 1
    _fields_ = [
        ('X', ctypes.c_uint8),
        ('Y', ctypes.c_uint8)
    ]


def create_point_array(coordinates):
    N = len(coordinates)  # number of points
    array_of_N_poonts = TPoint * N  # make a new "class" of array with N elements
    points = array_of_N_poonts()  # initialise an array variable
    #
    for ii, point in enumerate(points):
        x = coordinates[ii][0]
        y = coordinates[ii][1]
        points[ii].X = x
        points[ii].Y = y
    #
    return points


# TODO arbitrary slope line
def create_line(x0, y0, x1, y1):
    coordinates = []
    for ii in range(x1 - x0):
        coordinates.append([x0 + ii, y0])
    return coordinates


# TODO better definition of rectangle
def create_rectangle(x0, y0, x1, y1):
    coordinates = []
    Nx = x1 - x0
    Ny = y1 - y0
    for ii in range(Nx):
        for jj in range(Ny):
            coordinates.append([x0 + ii, y0 + jj])
    return coordinates


class Bruker():
    def __init__(self, path_to_dll):
        self.path_to_dll = path_to_dll
        try:
            self.bruker = ctypes.cdll.LoadLibrary(path_to_dll)
            print(path_to_dll, self.bruker)
        except:
            print(f'path to dll {path_to_dll} does not exist')

    def initialise(self):
        output = self.bruker.InitializeIOScan()  # establishes connection between IOScan device and user program.
        if output == 0:
            # no error
            print('Connection to Bruker API established')
        else:
            print('Connection failed')

    def get_image_configuration_properties(self):
        # ImageWidth,
        # ImageHeight,
        # PixelAverage,
        # LineAverage,
        # SEBitCount,
        # Contrast1,
        # Brightness1,
        # Contrast2,
        # Brightness2,
        # Tilt: TValueDescription;
        output = self.bruker.ImageGetConfigurationProperties()
        return output

    def get_image_configuration(self):
        output = self.bruker.ImageGetConfiguration()
        return output

    def set_image_configuration(self, image_width=256, image_height=256, pixel_average=1, line_average=1,
                                bit_depth=12,
                                input_1_used=True, input_2_used=False, power_sync_used=False, counter_used=False,
                                counter_index=0, active_counters=0,
                                tilt_angle=0, tilt_direction=0,
                                counter_mode=0, pixel_time=1):
        # ImageSetConfiguration(256,256,1,1,12,
        #                       true,false,false,false,
        #                       0,0,0,0,
        #                       cmw,pt);
        # ImageWidth,   Number of pixels in horizontal direction
        # ImageHeight,  Number of pixels in vertical direction
        # PixelAverage, Number of pixel average cycles
        # LineAverage,  Number of line average cycles
        # SEBitcount: word;   Use input channel 1 for scan
        # Input1Used,         Use input channel 2 for scan
        # Input2Used,         Use power synchronization for scan
        # PowerSyncUsed,      Use counters for scan
        # CounterUsed: boolean;
        # CounterIndex       Index of counter mode according to counter mode strings
        # ActiveCounters: word;    Used counters for scanning, every bit set signals an active counter
        # TiltAngle: integer;     Current sample tilt
        # TiltDirection: byte;  Current tilt direction 0 = no tilt; 1 = tilt in X direction; 2 = tilt in Y direction
        # return var CounterModeWord: word; Return value to set the counter mode
        # return var PixelTime: word): integer; Return value for the pixel time according to the number of input channels used

        print('setting the imaging parameters')
        output = self.bruker.ImageSetConfiguration(image_width=image_width, image_height=image_height,
                                                   pixel_average=pixel_average, line_average=line_average,
                                                   bit_depth=bit_depth,
                                                   input_1_used=input_1_used, input_2_used=input_2_used,
                                                   power_sync_used=power_sync_used, counter_used=counter_used,
                                                   counter_index=counter_index, active_counters=active_counters,
                                                   tilt_angle=tilt_angle, tilt_direction=tilt_angle,
                                                   counter_mode=counter_mode, pixel_time=pixel_time)
        print(output)

    def set_point(self, x=10, y=20):
        # set beam position
        point = TPoint(x, y)
        output = self.bruker.ImageSetPoint(point)
        print(f'setting point ({x}, {y}) output=', output)

    def get_point(self):
        point = self.bruker.ImageGetPoint()
        print('point set to ', point)

    def set_points_list(self, coordinates):
        # set list of beam positions
        N = len(coordinates)
        points = create_point_array(coordinates)
        output = self.bruker.ImageSetPointList(N, points)
        print(output, '; setiing an array of points coordinates')

    def set_scan_mode(self, type='set_point'):
        # 0 = normal image scan
        # 1 = ‘SetPoint’ is used to change scan position
        # 2 = external triggered scan (TTL input)
        if type == 'nornal' or type == 0:
            output = self.bruker.ImageSetAcquisitionMode(0)
            print(output, '; set scan mode to 0:nornal')
        elif type == 'set_point' or type == 'setpoint' or type == 1:
            output = self.bruker.ImageSetAcquisitionMode(1)
            print(output, '; set scan mode to 1:SetPoint')
        elif type == 'external' or type == 2:
            output = self.bruker.ImageSetAcquisitionMode(2)
            print(output, '; set scan mode to 2:external TTL')
        else:
            output = self.bruker.ImageSetAcquisitionMode(0)
            print(output, '; Error in scanning mode settings, setting to nornal mode')

    def get_scan_mode(self):
        # 0 = normal image scan
        # 1 = ‘SetPoint’ is used to change scan position
        # 2 = external triggered scan (TTL input)
        output = self.ImageGetAcquisitionMode()
        print('Acquisition mode = ', output)

    def start_scan(self):
        output = self.bruker.ImageStart()
        print(output, '; scan started')

    def stop_scan(self, stop_position=0):
        # determines where to stop the scan:
        # 0 = immediately
        # 1 = end of current segment
        # 2 = end of last segment
        output = self.bruker.ImageStop(stop_position)
        print(output, '; scan stopped')

    def get_scan_state(self):
        # current scan state:
        # 0 = scan stopped
        # 1 = scan running
        # 2 = wait for scan to stop
        output = self.bruker.ImageGetState()
        print('current scan state = ', output)

    def set_SEM_to_external_mode(self, external=False):
        # true: set SEM to external scan
        # false: set SEM to internal scan
        output = self.bruker.ImageSetSEMExternMode(external)
        print(output, '; setting external SEM mode to ', str(external))

    def get_SEM_external_mode(self):
        output = self.bruker.ImageGetSEMExternMode()
        print(output, '; SEM mode is set to ', output)

    def get_line_data(self, Y, line_length=256):
        # PixelPtr	   : TWordArray;
        # res:=ImageGetLine(Channel,aSeg,@PixelPtr[0],LineCounter);
        # (ImageChannel: byte;                # Image channel to use, ‘1’ is first
        # const Segment: TLineSegment;        # Segment to read data for
        # LineBuffer: PWordArray;             # Data buffer for line data
        # var Line Counter: DWord): integer;  # number of line scans for that line

        channel = 1
        line_segment = TSegment(Y, 0, line_length)  # Segment to read data for
        line_counter = 1  # number of line scans for that line
        #
        Pixel_Array = ctypes.c_uint8 * line_length
        pixel_array = Pixel_Array()
        pixel_ptr = ctypes.pointer(pixel_array)  # Data buffer for line data

        output = self.bruker.ImageGetLine(channel, line_segment, pixel_ptr, line_counter)
        print(output, '; line data copied to pixel_ptr')


if __name__ == '__main__':
    bruker = Bruker(path_to_dll=path_to_dll)
    bruker.initialise()
    bruker.get_image_configuration_properties()
    bruker.get_image_configuration()
    bruker.set_image_configuration(256, 256, 1, 1, 12, True, False, False, False, 0, 0, 0, 0, 0, 1)
    bruker.set_image_configuration()

    bruker.set_point(5, 7)
    bruker.get_point()
    bruker.set_scan_mode(type=1)
    # bruker.get_scan_mode() # ERROR 'Bruker' object has no attribute 'ImageGetAcquisitionMode

    coordinates = [[1, 2], [3, 4], [5, 6], [7, 8]]
    points = create_point_array(coordinates)
    bruker.set_points_list(coordinates)

    coordinates = create_rectangle(x0=1, y0=1, x1=200, y1=200)
    points_rectangular_scan = create_point_array(coordinates)
    bruker.set_points_list(coordinates)

    bruker.start_scan()
    bruker.get_scan_state()
    time.sleep(0.2)
    bruker.stop_scan()
    bruker.get_scan_state()

    bruker.set_SEM_to_external_mode(external=False)
    bruker.get_SEM_external_mode()

    ### TODO read lines into pointer array
    segment = TSegment(100, 0, 256)
    length_of_array = 6
    Pixel_Array = ctypes.c_uint8 * length_of_array
    # np.random.randint(0, 255, [1,10])
    pixel_array = Pixel_Array(255, 254, 253, 25, 20, 15)
    pixel_ptr = ctypes.pointer(pixel_array)
    pixel_ptr[0]

    bruker.get_line_data(Y=100, line_length=256)

