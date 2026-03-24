import os
import sys
import uuid
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
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

def convert_audio(input_file, output_path, is_temp=False):
    """
    共用的 FFmpeg 轉換處理函數，直接輸出符合以下規格的 WAV 音訊檔案：
      單聲道 (Mono)
      32kHz 採樣率
      16-bit PCM 格式
      自動正規化音量(避免聲音過小或破音)
    """
    try:
        cmd = [
            ffmpeg_exe, "-y", "-i", input_file,
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
            
        if is_temp:
            try:
                if os.path.exists(input_file):
                    os.remove(input_file)
            except Exception:
                pass
                
        return True, "轉換成功！"
    except Exception as e:
        return False, str(e)

def select_tts_output():
    filepath = filedialog.asksaveasfilename(
        title="儲存 WAV 檔案",
        defaultextension=".wav",
        filetypes=(("WAV 檔案", "*.wav"), ("所有檔案", "*.*"))
    )
    if filepath:
        tts_output_entry.delete(0, tk.END)
        tts_output_entry.insert(0, filepath)

def process_tts_conversion():
    input_text = tts_input_text.get("1.0", tk.END).strip()
    output_path = tts_output_entry.get()
    
    if not input_text or not output_path:
        messagebox.showwarning("警告", "請先輸入文字和選擇輸出檔案！")
        return
        
    try:
        tts_convert_btn.config(text="轉換中...", state=tk.DISABLED)
        root.update()
        
        temp_mp3 = f"temp_speech_{uuid.uuid4().hex}.mp3"
        tts = gTTS(text=input_text, lang='zh-tw')
        tts.save(temp_mp3)

        success, msg = convert_audio(temp_mp3, output_path, is_temp=True)
        
        if success:
            messagebox.showinfo("成功", "文字成功轉換為語音 WAV 檔！")
        else:
            messagebox.showerror("錯誤", f"轉換失敗：{msg}")
    except Exception as e:
        messagebox.showerror("錯誤", f"轉換失敗：{str(e)}")
    finally:
        tts_convert_btn.config(text="開始轉換", state=tk.NORMAL)

def select_mp3_input():
    filepath = filedialog.askopenfilename(
        title="選擇 MP3 檔案",
        filetypes=(("MP3 檔案", "*.mp3"), ("音訊檔案", "*.mp3 *.wav *.m4a *.aac"), ("所有檔案", "*.*"))
    )
    if filepath:
        mp3_input_entry.delete(0, tk.END)
        mp3_input_entry.insert(0, filepath)
        
        # Auto-fill output path if empty
        if not mp3_output_entry.get():
            base_path = os.path.splitext(filepath)[0]
            mp3_output_entry.insert(0, f"{base_path}_converted.wav")

def select_mp3_output():
    filepath = filedialog.asksaveasfilename(
        title="儲存 WAV 檔案",
        defaultextension=".wav",
        filetypes=(("WAV 檔案", "*.wav"), ("所有檔案", "*.*"))
    )
    if filepath:
        mp3_output_entry.delete(0, tk.END)
        mp3_output_entry.insert(0, filepath)

def process_mp3_conversion():
    input_path = mp3_input_entry.get()
    output_path = mp3_output_entry.get()
    
    if not input_path or not output_path:
        messagebox.showwarning("警告", "請先選擇輸入檔和輸出檔！")
        return
        
    if not os.path.exists(input_path):
        messagebox.showerror("錯誤", "找不到輸入的檔案！")
        return
        
    try:
        mp3_convert_btn.config(text="轉換中...", state=tk.DISABLED)
        root.update()
        
        success, msg = convert_audio(input_path, output_path, is_temp=False)
        
        if success:
            messagebox.showinfo("成功", "檔案成功轉換為 WAV 檔！")
        else:
            messagebox.showerror("錯誤", f"轉換失敗：{msg}")
    except Exception as e:
        messagebox.showerror("錯誤", f"轉換失敗：{str(e)}")
    finally:
        mp3_convert_btn.config(text="開始轉換", state=tk.NORMAL)

root = tk.Tk()
root.title("音訊處理與轉換工具 (文字/MP3轉WAV)")
root.geometry("520x290")
root.resizable(False, False)

# Create styles
style = ttk.Style()
style.theme_use('clam')
style.configure("TNotebook.Tab", font=("Arial", 11, "bold"), padding=[10, 5])

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both', padx=10, pady=10)

# ==================== TTS Tab ====================
tts_frame = ttk.Frame(notebook)
notebook.add(tts_frame, text="📝 文字轉語音")

tk.Label(tts_frame, text="輸入文字：").grid(row=0, column=0, padx=10, pady=15, sticky="ne")
tts_input_text = tk.Text(tts_frame, width=40, height=3, font=("Arial", 12))
tts_input_text.grid(row=0, column=1, padx=5, pady=15, columnspan=2)

tk.Label(tts_frame, text="儲存 WAV 路徑：").grid(row=1, column=0, padx=10, pady=5, sticky="e")
tts_output_entry = tk.Entry(tts_frame, width=32, font=("Arial", 10))
tts_output_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
tk.Button(tts_frame, text="瀏覽...", command=select_tts_output, width=8).grid(row=1, column=2, padx=5, pady=5)

tts_convert_btn = tk.Button(tts_frame, text="開始轉換", command=process_tts_conversion, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
tts_convert_btn.grid(row=2, column=0, columnspan=3, pady=15)

# ==================== MP3 to WAV Tab ====================
mp3_frame = ttk.Frame(notebook)
notebook.add(mp3_frame, text="🎵 音訊檔轉 WAV")

tk.Label(mp3_frame, text="選擇來源檔案：").grid(row=0, column=0, padx=10, pady=25, sticky="e")
mp3_input_entry = tk.Entry(mp3_frame, width=32, font=("Arial", 10))
mp3_input_entry.grid(row=0, column=1, padx=5, pady=25, sticky="w")
tk.Button(mp3_frame, text="瀏覽...", command=select_mp3_input, width=8).grid(row=0, column=2, padx=5, pady=25)

tk.Label(mp3_frame, text="儲存 WAV 路徑：").grid(row=1, column=0, padx=10, pady=5, sticky="e")
mp3_output_entry = tk.Entry(mp3_frame, width=32, font=("Arial", 10))
mp3_output_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
tk.Button(mp3_frame, text="瀏覽...", command=select_mp3_output, width=8).grid(row=1, column=2, padx=5, pady=5)

mp3_convert_btn = tk.Button(mp3_frame, text="開始轉換", command=process_mp3_conversion, bg="#2196F3", fg="white", font=("Arial", 12, "bold"))
mp3_convert_btn.grid(row=2, column=0, columnspan=3, pady=20)

root.mainloop()
