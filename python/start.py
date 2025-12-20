from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QMenu
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor
import subprocess, os, sys

STATUS_FILE = "loader.status"

class FloatingSwitch(QWidget):
    def __init__(self):
        super().__init__()
        self.proc = None
        self.checked = False
        self.drag_pos = None

        # 設定視窗：無邊框、工具視窗（不在工作列顯示）、最上層、背景透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(200, 80) # 稍微加寬以容納文字
        self.setCursor(Qt.PointingHandCursor)

        # 狀態標籤
        self.tooltip = QLabel(self)
        self.tooltip.setGeometry(5, 35, 190, 30)
        self.tooltip.setStyleSheet("color: #FF3B30; font: bold 10pt 'Microsoft JhengHei';")
        self.tooltip.setText("服務已停止")

        # 定時器：監控進程狀態與讀取文件
        self.timer = QTimer()
        self.timer.timeout.connect(self.monitor_service)
        self.timer.start(500)

    def monitor_service(self):
        # 檢查子進程是否意外結束
        if self.proc and self.proc.poll() is not None:
            self.proc = None
            self.checked = False
            self.update()

        # 更新文字狀態
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    self.tooltip.setText(content if content else "運行中...")
            except:
                pass
        else:
            if not self.checked:
                self.tooltip.setText("服務已停止")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.checked = not self.checked
            if self.checked:
                self.start_service()
            else:
                self.stop_service()
            self.update()
        elif event.button() == Qt.RightButton:
            # 記錄右鍵點擊位置以便拖動
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.RightButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)

    def contextMenuEvent(self, event):
        # 右鍵選單，方便關閉整個程式
        menu = QMenu(self)
        exit_action = menu.addAction("退出程式")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == exit_action:
            self.close()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        # 繪製背景軌道
        bg_color = QColor("#34C759") if self.checked else QColor("#E5E5EA")
        p.setBrush(bg_color)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, 60, 30, 15, 15)
        
        # 繪製白色圓鈕
        p.setBrush(QColor("white"))
        knob_x = 30 if self.checked else 0
        p.drawEllipse(knob_x, 0, 30, 30)

    def start_service(self):
        if self.proc is None:
            creation_flags = 0
            if os.name == "nt":
                creation_flags = subprocess.CREATE_NO_WINDOW
            
            # 使用 sys.executable 確保環境一致
            self.proc = subprocess.Popen(
                [sys.executable, "loader.py"], 
                creationflags=creation_flags
            )

    def stop_service(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait() # 等待進程完全退出
            self.proc = None
            # 停止後可選擇刪除狀態檔
            if os.path.exists(STATUS_FILE):
                try: os.remove(STATUS_FILE)
                except: pass

    def closeEvent(self, event):
        # 關閉視窗時務必殺掉子進程
        self.stop_service()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = FloatingSwitch()
    w.move(100, 100)
    w.show()
    sys.exit(app.exec_())