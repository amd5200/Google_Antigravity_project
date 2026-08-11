import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JPG 圖片批次縮小工具")
        self.root.geometry("620x520")
        self.root.minsize(550, 480)

        # 訊息佇列 (線程安全 UI 更新)
        self.msg_queue = queue.Queue()

        # UI 樣式設定
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self._setup_ui()
        self._check_queue()

    def _setup_ui(self):
        # 主容器面板
        main_frame = ttk.Frame(self.root, padding="15 15 15 15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 區塊 1: 資料夾與路徑設定
        folder_lf = ttk.LabelFrame(main_frame, text=" 1. 資料夾設定 ", padding="10 10 10 10")
        folder_lf.pack(fill=tk.X, pady=(0, 10))

        # 目標資料夾
        ttk.Label(folder_lf, text="目標資料夾：").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.src_folder_var = tk.StringVar()
        src_entry = ttk.Entry(folder_lf, textvariable=self.src_folder_var, width=42)
        src_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        browse_src_btn = ttk.Button(folder_lf, text="瀏覽...", command=self.browse_src_folder)
        browse_src_btn.grid(row=0, column=2, padx=5, pady=5)

        # 輸出方式設定
        ttk.Label(folder_lf, text="儲存位置：").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.save_mode_var = tk.StringVar(value="subfolder")
        
        mode_frame = ttk.Frame(folder_lf)
        mode_frame.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=5)
        
        ttk.Radiobutton(mode_frame, text="另存至子資料夾 (resized)", value="subfolder", variable=self.save_mode_var).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(mode_frame, text="覆蓋原始檔案", value="overwrite", variable=self.save_mode_var).pack(side=tk.LEFT)

        folder_lf.columnconfigure(1, weight=1)

        # 區塊 2: 縮小比例與品質設定
        setting_lf = ttk.LabelFrame(main_frame, text=" 2. 縮小設定 ", padding="10 10 10 10")
        setting_lf.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(setting_lf, text="縮小至原始大小的百分比 (%)：").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.scale_var = tk.StringVar(value="50")
        scale_spin = ttk.Spinbox(setting_lf, from_=1, to=100, textvariable=self.scale_var, width=8)
        scale_spin.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(setting_lf, text="(範圍: 1 ~ 100，例如 50 表示縮小為 50%)", foreground="#666666").grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # 區塊 3: 執行按鈕與進度
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))

        self.start_btn = ttk.Button(action_frame, text="開始批次縮小圖片", command=self.start_processing)
        self.start_btn.pack(fill=tk.X, ipady=5)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(action_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(8, 0))

        # 區塊 4: 處理日誌紀錄
        log_lf = ttk.LabelFrame(main_frame, text=" 3. 處理日誌 ", padding="10 10 10 10")
        log_lf.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_lf, wrap=tk.WORD, state=tk.DISABLED, background="#fdfdfd", relief=tk.SOLID, borderwidth=1)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(log_lf, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def browse_src_folder(self):
        folder = filedialog.askdirectory(title="選擇圖片目標資料夾")
        if folder:
            self.src_folder_var.set(folder)

    def log(self, message):
        """將訊息推入佇列，由主線程異步寫入 UI"""
        self.msg_queue.put(("log", message))

    def update_progress(self, current, total):
        pct = (current / total) * 100 if total > 0 else 0
        self.msg_queue.put(("progress", pct))

    def set_button_state(self, enabled):
        self.msg_queue.put(("state", enabled))

    def _check_queue(self):
        """定期檢查佇列訊息並更新 UI"""
        try:
            while True:
                msg_type, val = self.msg_queue.get_nowait()
                if msg_type == "log":
                    self.log_text.config(state=tk.NORMAL)
                    self.log_text.insert(tk.END, val + "\n")
                    self.log_text.see(tk.END)
                    self.log_text.config(state=tk.DISABLED)
                elif msg_type == "progress":
                    self.progress_var.set(val)
                elif msg_type == "state":
                    self.start_btn.config(state=tk.NORMAL if val else tk.DISABLED)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._check_queue)

    def start_processing(self):
        folder = self.src_folder_var.get().strip()
        scale_str = self.scale_var.get().strip()

        if not folder:
            messagebox.showwarning("輸入錯誤", "請先指定目標資料夾路徑！")
            return

        if not os.path.isdir(folder):
            messagebox.showerror("路徑無效", f"指定的資料夾不存在：\n{folder}")
            return

        try:
            scale_percent = float(scale_str)
            if not (0 < scale_percent <= 100):
                raise ValueError
        except ValueError:
            messagebox.showwarning("輸入錯誤", "請輸入有效的縮放百分比（數值範圍需介於 1 到 100 之間）。")
            return

        scale = scale_percent / 100.0
        save_mode = self.save_mode_var.get()

        # 清空日誌與進度條，停用按鈕
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.set_button_state(False)

        # 開啟背景工作線程
        worker_thread = threading.Thread(
            target=self._process_images_worker,
            args=(folder, scale, save_mode),
            daemon=True
        )
        worker_thread.start()

    def _process_images_worker(self, folder_path, scale, save_mode):
        try:
            supported_extensions = ('.jpg', '.jpeg')
            try:
                files = [f for f in os.listdir(folder_path) if f.lower().endswith(supported_extensions)]
            except Exception as e:
                self.log(f"無法讀取資料夾內容：{e}")
                return

            if not files:
                self.log("在指定資料夾中未找到任何 JPG/JPEG 圖片檔案。")
                return

            # 設定輸出目錄
            if save_mode == "subfolder":
                out_dir = os.path.join(folder_path, "resized")
                os.makedirs(out_dir, exist_ok=True)
                self.log(f"輸出目錄：{out_dir}")
            else:
                out_dir = folder_path
                self.log("注意：設定為覆蓋原始檔案。")

            total_files = len(files)
            self.log(f"共找到 {total_files} 個 JPG/JPEG 檔案。開始將圖片縮小至原始尺寸的 {int(scale * 100)}% ...\n")

            success_count = 0
            for idx, filename in enumerate(files, start=1):
                src_path = os.path.join(folder_path, filename)
                dst_path = os.path.join(out_dir, filename)

                try:
                    with Image.open(src_path) as img:
                        orig_w, orig_h = img.size
                        new_w = max(1, int(orig_w * scale))
                        new_h = max(1, int(orig_h * scale))

                        # 保持原始 EXIF (若有) 並重新繪製
                        resized_img = img.resize((new_w, new_h), Image.LANCZOS)
                        
                        # 儲存
                        exif = img.info.get('exif')
                        if exif:
                            resized_img.save(dst_path, quality=95, exif=exif)
                        else:
                            resized_img.save(dst_path, quality=95)

                        self.log(f"[{idx}/{total_files}] 已處理: {filename} ({orig_w}x{orig_h} -> {new_w}x{new_h})")
                        success_count += 1
                except Exception as e:
                    self.log(f"[{idx}/{total_files}] 處理失敗 {filename}：{e}")

                self.update_progress(idx, total_files)

            self.log(f"\n全部處理完成！成功數：{success_count} / {total_files}")
        finally:
            self.set_button_state(True)

def main():
    root = tk.Tk()
    app = ImageResizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()