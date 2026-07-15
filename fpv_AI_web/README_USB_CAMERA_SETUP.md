# USB Capture AI Object Detection - 系統設定與使用說明

本專案 (`usb_capture_object_detect.html`) 是一個透過手機瀏覽器，結合 USB 影像擷取卡（例如 AV 轉 USB 擷取卡）進行第一人稱視角 (FPV) 畫面輸入，並利用 TensorFlow.js (COCO-SSD) 進行即時 AI 物件辨識的 Web 應用程式。

此網頁還內建了 **Google Cardboard VR 雙螢幕模式**，讓您可以透過手機體驗沉浸式的 FPV 結合 AI 辨識畫面。

---

## 🔧 硬體連接步驟

1. 將 FPV 的 AV 接收器影像輸出，連接到 **「AV 轉 USB 擷取卡」** 上。
2. 使用 **OTG 轉接頭** 將 USB 擷取卡連接到您的 Android 手機（或支援外接鏡頭的平板）。

---

## ⚠️ 解決「Camera error: Permission denied」問題

**為何會發生這個錯誤？**
現代手機瀏覽器 (Chrome, Safari 等) 基於安全隱私考量，要求調用相機鏡頭 (`getUserMedia` API) **必須在 HTTPS 加密連線或 localhost 環境下**才能執行。
如果您直接在手機上開啟這個 HTML 檔案 (網址列顯示 `file:///` )，或是透過一般的 HTTP 區域網路連線，瀏覽器會直接封鎖相機權限並跳出 Permission denied 錯誤。

您可以選擇以下 **三種解決方案** 的其中一種來執行本網頁：

### 方案一：上傳至免費 HTTPS 網頁代管服務 (最穩定推薦 ⭐)
這是最一勞永逸的方法，不需每次重新設定手機。
1. 將 `usb_capture_object_detect.html` 檔案上傳到如 **GitHub Pages**, **Vercel**, 或是 **Netlify** 等免費靜態網頁代管平台。
2. 取得平台提供的 `https://...` 網址。
3. 直接用手機瀏覽器開啟該網址，就會正常跳出「允許使用相機」的提示。

### 方案二：在手機 Chrome 強制允許不安全的 IP (適合區域網路測試)
如果您只是想透過電腦開啟 Local Server 並用手機連線測試：
1. 在您的電腦上，開啟命令提示字元 (Terminal) 並進入此網頁檔案所在的資料夾。
2. 執行 Python 內建的本地伺服器指令：
   ```bash
   python -m http.server 8000
   ```
3. 拿起您的 **Android 手機**，打開 Chrome 瀏覽器，在網址列輸入：
   ```text
   chrome://flags/#unsafely-treat-insecure-origin-as-secure
   ```
4. 在該設定畫面的文字框中，輸入您電腦的區域網路 IP (例如：`http://192.168.1.100:8000`)。
5. 將右邊的下拉式選單改為 **Enabled**。
6. 點擊畫面右下角的 **Relaunch** 重啟瀏覽器。
7. 重啟後，在手機網址列輸入 `http://192.168.1.100:8000/usb_capture_object_detect.html`，Chrome 就會將此網址視為安全並放行相機權限了。

### 方案三：使用 Ngrok 建立安全的 HTTPS 通道 (進階測試)
1. 在電腦端啟動 Local Server（同方案二）。
2. 下載並執行 [Ngrok](https://ngrok.com/)。
3. 在命令提示字元輸入以下指令：
   ```bash
   ngrok http 8000
   ```
4. Ngrok 會產生一組隨機的 HTTPS 網址 (如 `https://xxxx.ngrok-free.app`)。
5. 用手機開啟這組網址即可順利連線並取得相機權限。

---

## 🎮 VR 雙螢幕模式使用說明

本網頁支援 Google Cardboard 雙螢幕顯示功能：
1. 成功允許相機權限後，可以在下拉選單中選擇您的 USB 擷取卡（名稱前方會有 🔌 符號標示），或選擇手機內建的前/後鏡頭。
2. 點擊 **「Start Camera」**，影像與 AI 辨識框會同步顯示在左右兩個畫布上。
3. 將手機轉為 **橫向 (Landscape)**。
4. 點擊紅色的 **「Enter VR Fullscreen」** 按鈕。
5. 畫面將會全螢幕顯示，此時請將手機放入 Google Cardboard 或其他 VR 眼鏡盒中，即可開始體驗！

---

## 🚀 近期功能優化與更新

* **調整攝影機解析度至 640x480**：為了減輕裝置在進行 AI 物件辨識時的運算負擔並提高整體的 FPS（每秒幀數）表現，已將系統預設向攝影機請求的理想解析度從原本的 1280x720 調整為 640x480。
* **新增畫布內建 FPS 顯示**：除了原先在介面下方的文字顯示外，現在在偵測畫面（Canvas）的左上角也會即時繪製目前的 FPS 數值。這項更新確保您在開啟「VR 雙螢幕模式」並進入全螢幕觀看時，依然能夠即時掌握畫面的流暢度。
* **新增原生 YUY2 影像格式離線版 (`usb_capture_object_detect_offline_yuy2.html`)**：為了解決部分 USB 影像擷取卡在瀏覽器中預設採用壓縮的 MJPEG 格式，因而產生額外解碼 CPU 運算負擔的問題，特別新增此版本。此版本藉由設定精確的 `640x480` 解析度約束，並加入 `resizeMode: "none"` 參數，強制瀏覽器直接對接並擷取硬體原生的 YUY2 未壓縮影像格式，以優化整體辨識效能。

---

## 📶 離線模式設定說明 (Offline Mode)

為了在沒有網路的環境（如戶外飛行場地）下也能正常使用 AI 辨識功能，本專案新增了離線運作支援：

### 1. 離線版檔案
* **`usb_capture_object_detect_offline.html`**：此檔案已預先設定為讀取本地資源。

### 2. 資源目錄結構
本系統已建立以下資料夾並下載必要檔案：
* **`js/`**：存放 AI 引擎與模型介面。
  - `tf.min.js` (TensorFlow.js)
  - `coco-ssd.js` (模型定義)
* **`models/coco-ssd/`**：存放離線 AI 模型。
  - `model.json` (模型架構)
  - `group1-shard1of5` ~ `group1-shard5of5` (權重數據)

### 3. 如何使用
1. 直接使用瀏覽器開啟 `usb_capture_object_detect_offline.html`。
2. 系統會自動從本地路徑載入 AI 模型（載入進度會顯示在「System Log」面板中）。
3. 即使在完全斷網的情況下，仍可順利進行 USB 擷取與物件辨識。

---

## 🛠️ USB 攝影機 / 擷取卡 疑難排解 (Troubleshooting)

如果您點擊 **「🔍 Probe USB Hardware」** 有看到裝置名稱，但 **「Camera Settings」** 選單中卻沒有出現該裝置，請嘗試以下步驟：

1. **檢查 Android OTG 設定**：
   * 部分手機（如 OPPO, Vivo, OnePlus）預設會關閉 OTG 功能。
   * 請至手機的「系統設定」，搜尋 **「OTG」** 並將其 **開啟**。
   
2. **解決電力不足問題 (特別是 Logitech 網路攝影機)**：
   * 網路攝影機 (Webcam) 的耗電量通常比單純的影像擷取卡高得多。
   * 如果手機供電不足，裝置雖然會出現在 USB 清單中，但 UVC 驅動程式會無法啟動。
   * **解決方案**：使用帶有供電功能的 OTG 轉接線 (Powered OTG Hub)，讓外部電源同時供電給攝影機。

3. **重新整理與權限**：
   * 插入裝置後，建議重新整理網頁。
   * 確保在彈出的視窗中點擊「允許 (Allow)」存取相機。

4. **確認 UVC 支援**：
   * 本專案依賴瀏覽器的標準 UVC (USB Video Class) 支援。
   * 絕大多數現代網路攝影機（如 Logitech C920, C270 等）與影像擷取卡都支援 UVC。如果是極早期的攝影機，可能無法運作。
