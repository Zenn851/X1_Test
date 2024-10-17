import os
import tkinter as tk
from tkinter import messagebox
import cv2
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
        if not self.video_files:
            messagebox.showerror("Error", "No MP4 files found in the current directory.")
            self.root.destroy()
            return

        self.current_video_index = 0
        self.cap = None
        self.playing = True

        self.label = tk.Label(self.root, bg="black")
        self.label.pack(fill=tk.BOTH, expand=True)

        self.next_button = tk.Button(self.root, text="Next Video", command=self.next_video, font=("Arial", 14))
        self.next_button.pack(side=tk.RIGHT, padx=20, pady=20)

        self.exit_button = tk.Button(self.root, text="Exit", command=self.exit_app, font=("Arial", 14))
        self.exit_button.pack(side=tk.LEFT, padx=20, pady=20)

        self.video_thread = threading.Thread(target=self.play_video)
        self.video_thread.daemon = True
        self.video_thread.start()

    def play_video(self):
        while True:
            if self.cap is None or not self.cap.isOpened():
                self.load_video(self.video_files[self.current_video_index])

            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            image_tk = ImageTk.PhotoImage(image)

            self.label.config(image=image_tk)
            self.label.image = image_tk

            time.sleep(1 / 30)  # Assuming 30 FPS

    def load_video(self, video_path):
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(video_path)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def next_video(self):
        self.current_video_index = (self.current_video_index + 1) % len(self.video_files)
        self.load_video(self.video_files[self.current_video_index])

    def exit_app(self):
        self.playing = False
        if self.cap is not None:
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FullScreenVideoApp(root)
    root.mainloop()
