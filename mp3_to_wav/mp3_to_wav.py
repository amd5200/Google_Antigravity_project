import os
import sys
import uuid
import tkinter as tk
from tkinter import filedialog, messagebox
import pydub
import imageio_ffmpeg
from gtts import gTTS
import subprocess

# Set the ffmpeg executable from imageio-ffmpeg for pydub to use natively
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
pydub.AudioSegment.converter = ffmpeg_exe

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def select_output():
    filepath = filedialog.asksaveasfilename(
        title="儲存 WAV 檔案",
        defaultextension=".wav",
        filetypes=(("WAV 檔案", "*.wav"), ("所有檔案", "*.*"))
    )
    if filepath:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, filepath)

def process_conversion():
    input_text = input_entry.get("1.0", tk.END).strip()
    output_path = output_entry.get()
    
    if not input_text or not output_path:
        messagebox.showwarning("警告", "請先輸入文字和選擇輸出檔案！")
        return
        
    try:
        # 變更按鈕狀態為轉換中
        convert_btn.config(text="轉換中...", state=tk.DISABLED)
        root.update()
        
        # 1. 先生出 MP3
        temp_mp3 = f"temp_speech_{uuid.uuid4().hex}.mp3"
        tts = gTTS(text=input_text, lang='zh-tw')
        tts.save(temp_mp3)

        # 2. 用 ffmpeg 把 MP3 轉成 WAV
        # -ac 1: 單聲道 (Mono)
        # -ar 32000: 採樣率 32kHz
        # -c:a pcm_s16le: 16-bit PCM 格式
        # -af loudnorm=I=-16:TP=-1.5:LRA=11: 自動正規化音量，提升響度並防止破音
        cmd = [
            ffmpeg_exe, "-y", "-i", temp_mp3,
            "-ac", "1",
            "-ar", "32000",
            "-c:a", "pcm_s16le",
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            output_path
        ]
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        
        if result.returncode != 0:
            raise Exception(result.stderr.decode('utf-8', errors='ignore'))
        # 確保刪除成功 (可選：如果檔案鎖定忽略例外)
        try:
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
        except Exception:
            pass
        
        messagebox.showinfo("成功", "文字成功轉換為語音 WAV 檔！")
    except Exception as e:
        messagebox.showerror("錯誤", f"轉換失敗：{str(e)}")
    finally:
        convert_btn.config(text="開始轉換", state=tk.NORMAL)

root = tk.Tk()
root.title("文字轉語音(WAV)轉換器")
root.geometry("480x250")
root.resizable(False, False)

# UI 介面設計
tk.Label(root, text="輸入文字：").grid(row=0, column=0, padx=10, pady=20, sticky="ne")
input_entry = tk.Text(root, width=40, height=3, font=("Arial", 12))
input_entry.grid(row=0, column=1, padx=5, pady=20, columnspan=2)

tk.Label(root, text="儲存 WAV 路徑：").grid(row=1, column=0, padx=10, pady=5, sticky="e")
output_entry = tk.Entry(root, width=30)
output_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
tk.Button(root, text="瀏覽...", command=select_output).grid(row=1, column=2, padx=5, pady=5)

convert_btn = tk.Button(root, text="開始轉換", command=process_conversion, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
convert_btn.grid(row=2, column=0, columnspan=3, pady=20)

root.mainloop()
