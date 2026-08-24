import threading
import time

import customtkinter

from config import *
from button_callbacks import *


class MainProgram(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry(str(int(SCREEN_WIDTH/1.5))+'x'+ str(int(SCREEN_HEIGHT/1.5)))

        # Button Callbacks
        self.button_callback = Callbacks(self)

        # App logic flags
        self.clip_key_pressed = False
        self.popup_active = False

        # GUI lists
        self.monitor_list = []
        self.clip_length_list = ['10','20','30','60','120']
        self.fps_list = ['24','30','60','120']

        # SCT
        self.sct = mss.MSS()
        self.video_list = []
        self.monitor = None
        self.last_frame_time = time.time()
        self.capture_start = 0
        self.capture_end = 0

        # Main Sidebar Frame (Vertical Stack)
        self.sidebar = customtkinter.CTkFrame(self, width=400, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)

        # --- ROW 1: Select Button + Current Key ---
        self.row1 = customtkinter.CTkFrame(self.sidebar, fg_color="transparent")
        self.row1.pack(side="top", anchor="w", padx=10, pady=10)

        self.choose_clipping_key = customtkinter.CTkButton(
            self.row1,
            text="Select Clip Button",
            command=self.button_callback.setbutton,
        )
        self.choose_clipping_key.pack(side="left", padx=5)

        self.current_button_text = customtkinter.CTkTextbox(
            self.row1, width=200, height=30
        )
        self.current_button_text.pack(side="left", padx=5)
        self.current_button_text.insert(
            index=0.0, text=("Current Key: " + str(self.button_callback.clipping_key))
        )
        self.current_button_text.configure(state="disabled")

        # --- MONITOR DATA LOGIC ---
        for monitor in range(len(self.sct.monitors) - 1):
            monitor_num = str(monitor)
            self.monitor_list.append(monitor_num)

        # --- ROW 2: Monitor Label + Dropdown ---
        self.row2 = customtkinter.CTkFrame(self.sidebar, fg_color="transparent")
        self.row2.pack(side="top", anchor="w", padx=10, pady=10)

        self.current_monitor_text = customtkinter.CTkTextbox(
            self.row2, width=200, height=30
        )
        self.current_monitor_text.pack(side="left", padx=5)
        self.current_monitor_text.insert(index=0.0, text="Monitor: ")
        self.current_monitor_text.configure(state="disabled")

        self.monitor_selector = customtkinter.CTkComboBox(
            self.row2,
            values=self.monitor_list,
            command=self.button_callback.selectmonitor,
            state="readonly",
        )
        self.monitor_selector.set(self.read_from_file("monitor"))
        self.monitor_selector.pack(side="left", padx=5)

        # --- ROW 3: Clip Length Dropdown ---
        self.row3 = customtkinter.CTkFrame(self.sidebar, fg_color="transparent")
        self.row3.pack(side="top", anchor="w", padx=10, pady=10)

        self.clip_length_text = customtkinter.CTkTextbox(self.row3, width=200, height=30)
        self.clip_length_text.pack(side="left", padx=5)
        self.clip_length_text.insert(index=0.0, text="Clip Length: ")
        self.clip_length_text.configure(state="disabled")

        self.clip_length_selector = customtkinter.CTkComboBox(
            self.row3,
            values=self.clip_length_list,
            command=self.button_callback.select_clip_length,
            state="readonly",
        )
        self.clip_length_selector.set(self.read_from_file("clip_length"))
        self.clip_length_selector.pack(side="left", padx=5)

        # --- Row 4: FPS Selection ---
        self.row4 = customtkinter.CTkFrame(self.sidebar, fg_color="transparent")
        self.row4.pack(side="top", anchor="w", padx=10, pady=10)

        self.fps_text = customtkinter.CTkTextbox(self.row4, width=200, height=30)
        self.fps_text.pack(side="left", padx=5)
        self.fps_text.insert(index=0.0, text="FPS: ")
        self.fps_text.configure(state="disabled")

        self.fps_selector = customtkinter.CTkComboBox(
            self.row4,
            values=self.fps_list,
            command=self.button_callback.select_fps,
            state="readonly",
        )
        self.fps_selector.set(self.read_from_file("fps"))
        self.fps_selector.pack(side="left", padx=5)


        # --- Row 5: Gpu Choice Selection ---
        self.row5 = customtkinter.CTkFrame(self.sidebar, fg_color="transparent")
        self.row5.pack(side="top", anchor="w", padx=10, pady=10)

        self.gpu_text = customtkinter.CTkTextbox(self.row5, width=200, height=30)
        self.gpu_text.pack(side="left", padx=5)
        self.gpu_text.insert(index=0.0, text="GPU: ")
        self.gpu_text.configure(state="disabled")

        # Makes sure a GPU is definitely selected
        if not self.read_from_file('gpu') in GPU_LIST:
            self.button_callback.select_gpu(GPU_LIST[0])

        self.gpu_selector = customtkinter.CTkComboBox(
            self.row5,
            values=GPU_LIST,
            command=self.button_callback.select_gpu,
            state="readonly",
        )
        self.gpu_selector.set(self.read_from_file("gpu"))
        self.gpu_selector.pack(side="left", padx=5)


        print('Initialised GUI :)')

        self.get_ffmpeg_arguments()

        # Close to system tray
        self.system_tray_setup()
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.loop() # The program logic

        # The mainloop that repeats the code above and keeps the window alive
        self.mainloop()

    # This is the program's main logic loop
    def loop(self):
        # print('Called mainloop')
        if keyboard.is_pressed(self.button_callback.clipping_key) and self.clip_key_pressed == False:
            print('Clipping...')
            Popup('Clipping...')

            # Compiling the list into a video clip
            frames_to_compile = list(self.video_list)
            self.last_frame_time = time.time()
            compilation_thread = threading.Thread(target=self.compile_clip,
                                                  args=(frames_to_compile,),
                                                  daemon = True)
            compilation_thread.start()

            self.clip_key_pressed = True

        elif not keyboard.is_pressed(self.button_callback.clipping_key):
            self.clip_key_pressed = False

        self.capture_screen()
        self.after(1,self.loop) # Lets the program logic mainloop keep running alongside GUI

    # Writes whatever the input is to wherever it needs to go
    def capture_screen(self):
        current_time = time.time()

        if self.capture_start == 0:
            self.capture_start = current_time

        # Defines the monitor
        self.monitor = self.sct.monitors[self.button_callback.monitor + 1]

        # Calculates frame delay to hit target fps
        elapsed_time = current_time - self.last_frame_time
        frame_delay = 1.0 / self.button_callback.fps

        if elapsed_time >= frame_delay:
            # Gets a screenshot and adds it to the list
            try:
                sct_image = self.sct.grab(self.monitor)
                self.video_list.append(sct_image.bgra)

            except:
                print('There was an error getting the screenshot! This is not good :(')

            # Culls unneeded screenshots
            if len(self.video_list) > self.button_callback.fps * self.button_callback.clip_length:
                self.video_list.pop(0)

            self.last_frame_time += frame_delay

# Puts all the screenshots together into a video
    def compile_clip(self,video_list):
        self.capture_end = time.time()

        actual_clip_length = self.capture_end - self.capture_start

        if actual_clip_length >= self.button_callback.clip_length:
            actual_clip_length = self.button_callback.clip_length

        actual_fps = len(video_list)/actual_clip_length
        actual_fps = int(round(actual_fps, 0))

        width = self.monitor['width']
        height = self.monitor['height']
        ffmpeg_cmd = [
            'bin/ffmpeg.exe',
            '-y',  # Overwrite output file if it already exists
            '-f', 'rawvideo',  # Input format is raw pixels
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'bgr0',  # MSS bgra data maps perfectly to FFmpeg's bgr0
            '-s', f"{width}x{height}",  # Tell FFmpeg the dimensions of the incoming frames
            '-r', str(actual_fps), # Input frame rate
            *self.get_ffmpeg_arguments(),
            self.button_callback.create_file_name()
        ]

        process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

        for image in video_list:
            process.stdin.write(image)

        process.stdin.close()
        process.wait()
        print('Clipped!')
        Popup('Clipped :)')

    def get_ffmpeg_arguments(self):
        gpu = self.button_callback.gpu.split()

        # AMD GPU
        if gpu[0] == 'AMD':
            return ('-i',
                    '-',
                    '-c:v',
                    'h264_amf',  # AMD Hardware Encoder
                    '-usage',
                    'lowlatency',  # Optimized for real-time capture
                    '-quality',
                    'speed',  # Prioritizes encoding speed
                    '-rc',
                    'cqp',  # Constant Quantization Parameter
                    '-qp_i',
                    '23',  # I-frame quality
                    '-qp_p',
                    '23',  # P-frame quality
                    '-pix_fmt',
                    'yuv420p')

        # Nvidia GPU
        elif gpu[0] == 'NVIDIA':
            return ('-i',
                    '-',
                    '-c:v',
                    'h264_nvenc',  # NVIDIA Hardware Encoder
                    '-preset',
                    'p1',  # P1 is the fastest performance preset
                    '-tune',
                    'll',  # Low Latency tuning
                    '-rc',
                    'constqp',  # Constant Quality mode
                    '-qp',
                    '23',  # Quality (18-28 is standard; lower = better quality)
                    '-pix_fmt',
                    'yuv420p')

        # Intel GPU
        elif gpu[0] == 'INTEL(R)':
            return('-i',
                    '-',
                    '-c:v',
                    'h264_qsv',  # Intel QuickSync Encoder
                    '-preset',
                    'veryfast',  # Fast encoding preset for QuickSync
                    '-global_quality',
                    '23',  # Target quality
                    '-pix_fmt',
                    'nv12'  # Optimal pixel format for QSV)
                   )
    # If the GPU name is malformed or unrecognized
        return('-i',
               '-',
               '-c:v',
               'libx264',  # Software CPU Encoder
               '-preset',
               'ultrafast',  # Dramatically reduces CPU work & encoding time
               '-crf',
               '23',  # Constant Rate Factor (Quality)
               '-pix_fmt',
               'yuv420p')

    @staticmethod
    def write_to_file(pointer, value):
        # print('Called Write to file')
        updated_file = []
        with open('defaults.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)

            for line in reader:
                if line[0] == pointer:
                    print('Written', value, 'to', pointer)
                    line[1] = value

                updated_file.append(line) # adds the line as a new component in the list

        # re-writes the file to put in the new values accurately
        with open('defaults.csv','w',newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(updated_file)

    @staticmethod
    def read_from_file(pointer):
        with open('defaults.csv','r') as csvfile:
            reader = csv.reader(csvfile)

            for line in reader:
                if line[0] == pointer:
                    return line[1]
            return None

    # Tray Logic ------------------------------------------------------------------------

    # Brings the window back up
    def show_window(self):
        self.deiconify()
        self.lift()

    # Hides the window
    def hide_window(self):
        self.withdraw()

    # Shuts down the app
    def quit_app(self,icon):
        icon.stop()
        self.quit()

    # Initialises the system tray logic
    def system_tray_setup(self):
        # Creates the menu and icon
        menu = pystray.Menu(pystray.MenuItem('Open',self.show_window),
                            pystray.MenuItem('Quit', self.quit_app))
        tray_icon = pystray.Icon('Clipping Software',TRAY_ICON,
                                 'Clipping Software', menu)

        # Runs it in a thread so it doesn't stop the rest of the program
        tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
        tray_thread.start()


# This is the popup that tells you your clipping
class Popup(customtkinter.CTkToplevel):
    def __init__(self, text):
        super().__init__()
        self.width = str(int(SCREEN_WIDTH / 7))
        self.height = str(int(SCREEN_HEIGHT / 11))
        self.text = text


        # Helps make it rounder
        self.config(background="pink")
        self.attributes('-transparentcolor','pink')
        frame = customtkinter.CTkFrame(self, width = int(self.width), height = int(self.height), fg_color='#545252', corner_radius=20)
        frame.pack(fill="both", expand=True)

        # Removes the title bar
        self.overrideredirect(True)
        self.attributes("-topmost", True)  # Keep on top

        text = customtkinter.CTkLabel(frame,text=text, font=("Arial", 16))
        text.pack(expand=True)

        self.geometry(self.width + 'x' + self.height)

        # Makes the popup spawn in the right place
        # Format: WidthxHeight+X_Offset+Y_Offset
        # 50 pixels from the left of the screen, 50 pixels down from the top
        self.geometry(self.width + "x" + self.height + "+" + str(SCREEN_WIDTH - int(self.width)) + "+" + str(
            SCREEN_HEIGHT - int(self.height) - int(SCREEN_HEIGHT / 1.2)))

        self.after(1500, self.destroy)


if __name__ == "__main__":
    program = MainProgram()
