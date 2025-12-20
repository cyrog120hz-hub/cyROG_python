import base64, os, time

STATUS_FILE = "loader.status"

def write_status(msg):
    """確保狀態能即時寫入檔案供 UI 讀取"""
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        f.write(msg)
        f.flush()

def run_loader():
    write_status("🟡 正在載入核心...")

    # 1. 檢查檔案是否存在
    if not os.path.exists("payload.cache"):
        write_status("❌ 錯誤：找不到 payload.cache")
        return

    # 2. 讀取並解碼
    try:
        with open("payload.cache", "r", encoding="utf-8") as f:
            b64_data = f.read().strip()
        
        if not b64_data:
            write_status("❌ 錯誤：快取檔案為空")
            return

        # 解碼 Base64
        code = base64.b64decode(b64_data).decode("utf-8")
        
        # 準備執行空間
        namespace = {}
        # 執行解碼後的代碼，將定義存入 namespace
        exec(code, namespace)
        
        # 3. 檢查並執行進入點
        if "main_logic" in namespace:
            write_status("🟢 核心啟動成功")
            namespace["main_logic"]() # 執行你那段印出星號的代碼
        else:
            write_status("⚠ 警告：找不到 main_logic")

    except Exception as e:
        write_status(f"❌ 崩潰：{str(e)}")
        print(f"Error: {e}")
        return

    # 4. 常駐運行，防止進程結束導致 UI 顯示「已停止」
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        write_status("🔴 服務已終止")

if __name__ == "__main__":
    # 只需要呼叫主函式即可，不要在外面存取內部變數
    run_loader()