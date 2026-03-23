@echo off
echo 安裝依賴套件...
pip install -r requirements.txt

echo.
echo 開始打包為 .exe 執行檔...
pyinstaller --noconsole --onefile --collect-all imageio_ffmpeg mp3_to_wav.py

echo.
echo 打包完成！執行檔位於 dist 資料夾下的 mp3_to_wav.exe。
pause
