import os
import tkinter as tk
from tkinter import messagebox
import imageio
from PIL import Image, ImageTk
import threading
import time

class FullScreenVideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MP4 Video Player")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        self.video_files = [f for f in os.listdir() if f.endswith(".mp4")]
        if len(self.video_files) < 3:
            messagebox.showerror("Error", "At least three MP4 files are required in the current directory.")
            self.root.destroy()
            return

        self.playing = True
        self.frame_lock = threading.Lock()

        # Create exit button
        self.exit_button = tk.Button(self.root, text="Exit", command=self.exit_app, font=("Arial", 20), height=2, width=20)
        self.exit_button.grid(row=0, column=0, columnspan=3, padx=20, pady=20)

        # Create labels for each video
        self.labels = [tk.Label(self.root, bg="black") for _ in range(3)]
        for i, label in enumerate(self.labels):
            label.grid(row=1, column=i, sticky="nsew")

        self.video_readers = [None] * 3
        self.video_threads = []

        # Start video threads for each video
        for i in range(3):
            self.load_video(i, self.video_files[i])
            thread = threading.Thread(target=self.play_video, args=(i,))
            thread.daemon = True
            thread.start()
            self.video_threads.append(thread)

    def play_video(self, index):
        while self.playing:
            with self.frame_lock:
                if self.video_readers[index] is None:
                    continue

                try:
                    frame = self.video_readers[index].get_next_data()
                except (EOFError, IndexError):
                    self.load_video(index, self.video_files[index])
                    continue

                frame = Image.fromarray(frame)
                image_tk = ImageTk.PhotoImage(frame)

                self.labels[index].config(image=image_tk)
                self.labels[index].image = image_tk

            time.sleep(1 / 30)  # Assuming 30 FPS

    def load_video(self, index, video_path):
        if self.video_readers[index] is not None:
            try:
                self.video_readers[index].close()
            except RuntimeError:
                pass
        self.video_readers[index] = imageio.get_reader(video_path)

    def exit_app(self):
        self.playing = False
        for reader in self.video_readers:
            if reader is not None:
                try:
                    reader.close()
                except RuntimeError:
                    pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FullScreenVideoApp(root)
    root.mainloop()
