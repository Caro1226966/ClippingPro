from config import *

class Callbacks:
    def __init__(self, main):
        self.main = main # Main Program link


        # Clipping key flags
        self.setbutton_pressed = False
        self.clipping_key = str(self.main.read_from_file('clip_key'))
        print([self.clipping_key])
        if self.clipping_key == '':
            self.clipping_key = 'f8'
            self.main.write_to_file(value='f8', pointer='clip_key')

        # Monitor selector flags
        try:
            self.monitor = int(self.main.read_from_file('monitor'))
        except ValueError:
            self.selectmonitor([0])

        # FPS
        try:
            self.fps = int(self.main.read_from_file('fps'))
        except ValueError:
            self.select_fps(60)

        # Clip Length
        try:
            self.clip_length = int(self.main.read_from_file('clip_length'))
        except ValueError:
            self.select_clip_length(60)

        # GPU
        self.gpu = str(self.main.read_from_file('gpu'))


    # Lets the user set the button. Changes text too
    def setbutton(self):

        if not self.setbutton_pressed:
            self.setbutton_pressed = True
            self.clipping_key = None # Resets the clipping key

            # Lets the user set their key
            while self.clipping_key is None:
                self.clipping_key = keyboard.read_key()

            # Changes the text to new values
            self.main.current_button_text.configure(state="normal")  # configure textbox to be not read-only
            self.main.current_button_text.delete("0.0", "end")  # delete all text
            self.main.current_button_text.insert(index=0.0,text=('Current Key: '+str(self.clipping_key))) # Insert new values
            self.main.current_button_text.configure(state="disabled")  # configure textbox to be read-only

            # Update the defaults.csv file
            self.main.write_to_file(value=self.clipping_key,pointer='clip_key')

            # Prints it just to be sure
            print(self.clipping_key)

            self.setbutton_pressed = False
            self.main.clip_key_pressed = True

    # For monitor selection
    def selectmonitor(self, choice):
        self.monitor = int(choice[-1])

        self.main.write_to_file('monitor',str(self.monitor))

    # For FPS selection
    def select_fps(self, choice):
        self.fps = int(choice)
        self.main.write_to_file('fps',self.fps)
        self.reset_capture_list()

    # For clip length selection
    def select_clip_length(self, choice):
        self.clip_length = int(choice)
        self.main.write_to_file('clip_length', str(self.clip_length))

        self.reset_capture_list()

    # For GPU selection
    def select_gpu(self, choice):
        self.gpu = choice
        self.main.write_to_file('gpu', str(self.gpu))

    # Creates an appropriate path and file name for the clip
    def create_file_name(self):
        videos_path = Path.home() / "Videos" / 'Clips_OWO'
        videos_path.mkdir(parents=True, exist_ok=True)
        file_path = videos_path / f"{time.time()}.mp4"

        return str(file_path)

    # Resets the capture logic
    def reset_capture_list(self):
        self.main.video_list = []
        self.main.capture_start = 0

