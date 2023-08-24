import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import yt_dlp
import re

# 1. download ffmpeg https://github.com/yt-dlp/FFmpeg-Builds,unzip to current folder,for 'ffmpeg_location': './ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe'
# 2. pip install yt-dlp
# 3. py downloader.py
# 4. test https://www.youtube.com/watch?v=tzD9OxAHtzU
class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        
        self.video_link_label = tk.Label(root, text="Video Link:")
        self.video_link_label.pack(pady=10)
        
        self.video_link_entry = tk.Entry(root, width=50)
        self.video_link_entry.pack(pady=5)
        
        self.quality_label = tk.Label(root, text="Select Quality:")
        self.quality_label.pack()
        
        self.quality_combo = ttk.Combobox(root, values=["High", "Medium", "Low"])
        self.quality_combo.pack(pady=5)
        
        self.download_button = tk.Button(root, text="Download Video", command=self.download_video)
        self.download_button.pack(pady=10)
        
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)
        
    def download_video(self):
        video_url = self.video_link_entry.get()
        selected_quality = self.quality_combo.get()
        
        if not video_url:
            messagebox.showerror("Error", "Please enter a video link")
            return
        
        ydl_opts = {
            'ffmpeg_location': './ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe',
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'progress_hooks': [self.update_progress],
        }
        
        if selected_quality == "High":
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        elif selected_quality == "Medium":
            ydl_opts['format'] = '18/22/best'
        elif selected_quality == "Low":
            ydl_opts['format'] = 'worst'
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            
    def update_progress(self, d):
        if d['status'] == 'downloading':
            percent_match = re.search(r'\d+\.\d+%', d['_percent_str'])  # Use regex to match percent strings
            if percent_match:
                progress_percent = float(percent_match.group().strip('% '))  # Extract the matching percent string and convert to float
                self.progress_bar['value'] = progress_percent
                self.root.update_idletasks()
        elif d['status'] == 'finished':
            self.progress_bar['value'] = 100.0
            messagebox.showinfo("Complete", "Video download finished!")


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
