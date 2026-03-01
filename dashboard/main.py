# main.py
import sys
from PyQt6.QtWidgets import QApplication
from frontend.dashboard import DashboardWindow
from backend.data_manager import DataManager

def main():
    app = QApplication(sys.argv)

    # 1. Init UI
    window = DashboardWindow()
    window.show()

    # 2. Init Backend
    backend = DataManager()
    
    # 3. Connect Backend to Frontend
    # This is where the magic happens: Signal -> Slot
    backend.data_updated.connect(window.update_ui)

    # 4. Start the Data Stream
    backend.start()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()