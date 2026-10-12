import subprocess

import customtkinter

from config import *
from button_callbacks import *


class MainProgram(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        # Window setup
        self.geometry('380x500')
        self.resizable(False, False)

        # Button Callbacks
        self.button_callback = Callbacks(self)

        # App logic flags
        self.clip_key_pressed = False
        self.popup_active = False

        # GUI lists
        self.monitor_list = []
        self.clip_length_list = ['10','20','30','60']
        self.fps_list = ['24','30','60']

        # Capture
        self.sct = mss.MSS()
        self.video_list = []
        self.monitor = None
        self.last_frame_time = time.time()
        self.capture_start = 0
        self.capture_end = 0
        self.clip_num = 0
        self.ffmpeg_process = None
        self.clipping = False

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

        # --- ROW 1.5 (trust) ---
        self.row1point5 = customtkinter.CTkFrame(self.sidebar, fg_color="transparent")
        self.row1point5.pack(side="top", padx=10, pady=10)

        self.visuals_text = customtkinter.CTkLabel(self.row1point5, text='--- Visuals ---', font=('Arial', 20))
        self.visuals_text.pack(side="left", pady=5, padx=5, anchor='center')

        # --- MONITOR DATA LOGIC ---
        self.monitor_list.append('-1')
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

        # --- Row 6: Mouse Active Choice ---
        self.row6 = customtkinter.CTkFrame(self.sidebar, fg_color="transparent")
        self.row6.pack(side="top", anchor="w", padx=10, pady=10)

        self.show_mouse_text = customtkinter.CTkTextbox(self.row6, width=200, height=30)
        self.show_mouse_text.pack(side="left", padx=5)
        self.show_mouse_text.insert(index=0.0, text="Mouse: ")
        self.show_mouse_text.configure(state="disabled")

        self.show_mouse_selector = customtkinter.CTkCheckBox(self.row6,command=self.button_callback.draw_mouse)
        self.show_mouse_selector.pack(side='left', padx = 5)

        # Toggles it to on if the mouse is on
        if self.button_callback.mouse_shown:
            self.show_mouse_selector.toggle()

        # --- ROW 6.5 (trust) ---
        self.row6point5 = customtkinter.CTkFrame(self.sidebar, fg_color="transparent")
        self.row6point5.pack(side="top", padx=10, pady=10)

        self.visuals_text = customtkinter.CTkLabel(self.row6point5, text='--- Audio ---', font=('Arial', 20))
        self.visuals_text.pack(side="left", pady=5, padx=5, anchor='center')


        print('Initialised GUI :)')

        # Initialisation of ffmpeg
        self.start_ffmpeg()

        # Close to system tray
        self.system_tray_setup()
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.loop() # The program logic

        # The mainloop that repeats the code above and keeps the window alive
        self.mainloop()

    # This is the program's main logic loop
    def loop(self):
        # print('Called mainloop')
        if keyboard.is_pressed(self.button_callback.clipping_key) and self.clip_key_pressed == False and not self.clipping:

            # Compiling the list into a video clip
            threading.Thread(target=self.compile_clip).start()
            self.clip_key_pressed = True

        elif not keyboard.is_pressed(self.button_callback.clipping_key):
            self.clip_key_pressed = False

        self.after(1,self.loop) # Lets the program logic mainloop keep running alongside GUI

    # Starts the background capture loop
    def start_ffmpeg(self):
        # Shuts down any old processes
        self.stop_ffmpeg()

        self.button_callback.reset_capture_list()

        # Gets the correct encoders
        encoder = self.get_ffmpeg_arguments()
        monitors = get_monitors()
        monitor_idx = int(self.button_callback.monitor)

        # 2. Extract coordinates and dimensions safely
        if monitor_idx < len(monitors):
            m = monitors[monitor_idx]
            offset_x, offset_y = m.x, m.y
            width, height = m.width, m.height
        else:
            # Fallback to primary monitor bounds if index is out of range
            offset_x, offset_y, width, height = 0, 0, 1920, 1080

        # Gets the correct clip length
        segments = str(int(self.button_callback.clip_length/2))

        # print('MONITOR: ' + str(self.button_callback.monitor))

        if self.button_callback.monitor == -1:
            monitor_settings = ["-i", 'desktop']
        else:
            monitor_settings = ["-offset_x", str(offset_x),
            "-offset_y", str(offset_y),
            "-video_size", f"{width}x{height}",
            "-i", 'desktop']

        # FFMPEG Flags
        ffmpeg_cmd = [
            "bin/ffmpeg.exe",
            "-y",
            "-thread_queue_size", "1024",
            "-fflags", "nobuffer+discardcorrupt",
            "-f", "gdigrab",
            "-draw_mouse", str(self.button_callback.mouse_shown),
            "-framerate", str(self.button_callback.fps),
            *monitor_settings,
            *encoder,
            "-g", str(self.button_callback.fps * 2),  # Forces a keyframe every 2 seconds
            "-keyint_min", str(self.button_callback.fps * 2),
            "-sc_threshold", "0",  # Disables automatic scene-change keyframes for clean cuts
            "-movflags", "+frag_keyframe+empty_moov+default_base_moof",
            "-f", "segment",
            "-segment_time", "2",  # Length of each ring file in seconds
            "-segment_wrap", segments,  # Total number of rotating files before it loops,
            os.path.join(self.button_callback.get_temp_directory().as_posix(), "ring_%d.mp4")
        ]

        try:
            self.ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print('Starting capture failed Error: ', e)


    # Stops the FFMPEG background capture
    def stop_ffmpeg(self):
        # Checks if an instance is running
        if hasattr(self, 'ffmpeg_process') and self.ffmpeg_process:

            # Starts the stopping
            self.ffmpeg_process.terminate()

            # Gives it 2 seconds to stop and kills it if it doesn't
            try:
                self.ffmpeg_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.ffmpeg_process.kill()


    def compile_clip(self):
        # Gets the temp dir
        temp_dir = Path(self.button_callback.get_temp_directory().as_posix())

        # Gets all files in that location
        file_list = list(temp_dir.glob('ring_*.mp4'))

        # Makes sure there are actually files in the location
        if not file_list:
            print('No clips to compile')
            return

        # sorts the files by time and writes the names  in order into a txt document
        file_list = sorted(file_list, key=lambda f: f.stat().st_mtime)
        manifest_path = temp_dir / 'temp_file_names.txt'
        valid_files = file_list[:-1]
        with open(manifest_path, 'w', encoding='utf-8') as txt_file:
            for file in valid_files:
                posix_path = file.as_posix()
                txt_file.write('file ' + posix_path + '\n')

        output_filename = self.button_callback.create_file_name()

        ffmpeg_cmd = [
            "bin/ffmpeg.exe", "-y",
            "-fflags", "+genpts",
            "-f", "concat",
            "-safe", "0",
            "-i", str(manifest_path),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "23",
            "-c:a", "copy",
            str(output_filename)
        ]

        try:
            Popup('Clipping...')
            print('Clipping...')
            self.clipping = True

            # subprocess.run blocks this worker thread until stitching is done
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

            Popup('Clipped!')
            print('Clipped successfully to:', output_filename)

            self.clipping = False

        except subprocess.CalledProcessError as e:
            print('Compiling of full clip failed! Error code:', e)
            Popup('Clipping Failed!')
            self.clipping = False

    # Gets the correct FFMPEG arguments per GPU
    def get_ffmpeg_arguments(self):
            gpu = self.button_callback.gpu.split()

            # AMD GPU
            if gpu[0] == 'AMD':
                return [
                    '-c:v', 'h264_amf',
                    '-rc', 'cbr',  # Switch away from vbr_latency
                    '-b:v', '5M',  # Stable constant bitrate
                    '-qp_i', '23',
                    '-qp_p', '23',
                    "-pix_fmt", "nv12",
                ]

            # NVIDIA GPU
            elif gpu[0] == 'NVIDIA':
                return [
                    '-c:v', 'h264_nvenc',
                    '-preset', 'p1',
                    '-tune', 'll',
                    '-rc', 'constqp',
                    '-qp', '23',
                    "-pix_fmt", "yuv420p",
                ]

            # Intel GPU
            elif gpu[0] == 'INTEL(R)':
                return [
                    '-c:v', 'h264_qsv',
                    '-preset', 'veryfast',
                    '-global_quality', '23',
                    "-pix_fmt", "yuv420p",
                ]

            # CPU Only / No GPU Fallback (libx264)
            return [
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-crf', '23',
                "-pix_fmt", "yuv420p",
            ]

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
        self.stop_ffmpeg()

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
