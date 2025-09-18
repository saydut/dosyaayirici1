import sys
import os
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QStatusBar
)
from PyQt6.QtCore import Qt


def extract_number(filename):
    """Dosya adındaki ilk numarayı döndürür, yoksa None"""
    match = re.search(r"\d+", filename)
    return match.group(0) if match else None


def extract_prefix(filename):
    """Dosya adındaki ilk numaradan önceki kısmı döndürür"""
    match = re.search(r"\d+", filename)
    if match:
        return filename[:match.start()]
    return filename


def extract_name_no_ext(filename):
    """Dosya adını uzantısız döndürür"""
    return os.path.splitext(filename)[0]


class FolderCompareApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📂 Klasör İçeriği Karşılaştırma - PyQt6")
        self.resize(800, 600)

        # Ana widget
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        # Klasör 1 seçimi
        folder1_layout = QHBoxLayout()
        folder1_layout.addWidget(QLabel("Klasör 1:"))
        self.folder1_edit = QLineEdit()
        folder1_layout.addWidget(self.folder1_edit)
        btn1 = QPushButton("Seç")
        btn1.clicked.connect(self.select_folder1)
        folder1_layout.addWidget(btn1)
        layout.addLayout(folder1_layout)

        # Klasör 2 seçimi
        folder2_layout = QHBoxLayout()
        folder2_layout.addWidget(QLabel("Klasör 2:"))
        self.folder2_edit = QLineEdit()
        folder2_layout.addWidget(self.folder2_edit)
        btn2 = QPushButton("Seç")
        btn2.clicked.connect(self.select_folder2)
        folder2_layout.addWidget(btn2)
        layout.addLayout(folder2_layout)

        # Karşılaştırma tipi
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Karşılaştırma Tipi:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Tam İsim", "Sadece Numara", "Sadece Önek"])
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # Karşılaştır butonu
        compare_btn = QPushButton("🔍 Karşılaştır")
        compare_btn.clicked.connect(self.compare_folders)
        layout.addWidget(compare_btn)

        # Sonuç tablosu
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Değer", "Eksik Olduğu Yer"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def select_folder1(self):
        folder = QFileDialog.getExistingDirectory(self, "Klasör 1 Seç")
        if folder:
            self.folder1_edit.setText(folder)

    def select_folder2(self):
        folder = QFileDialog.getExistingDirectory(self, "Klasör 2 Seç")
        if folder:
            self.folder2_edit.setText(folder)

    def compare_folders(self):
        folder1 = self.folder1_edit.text()
        folder2 = self.folder2_edit.text()
        mode = self.mode_combo.currentText()

        if not folder1 or not folder2:
            QMessageBox.critical(self, "Hata", "Lütfen iki klasör de seçin!")
            return

        try:
            files1 = os.listdir(folder1)
            files2 = os.listdir(folder2)

            if mode == "Tam İsim":
                set1 = set(extract_name_no_ext(f) for f in files1)
                set2 = set(extract_name_no_ext(f) for f in files2)
            elif mode == "Sadece Numara":
                set1 = set(filter(None, (extract_number(f) for f in files1)))
                set2 = set(filter(None, (extract_number(f) for f in files2)))
            elif mode == "Sadece Önek":
                set1 = set(extract_prefix(f) for f in files1)
                set2 = set(extract_prefix(f) for f in files2)
            else:
                set1 = set(files1)
                set2 = set(files2)

            only_in_folder1 = sorted(set1 - set2)
            only_in_folder2 = sorted(set2 - set1)

            self.table.setRowCount(0)  # Temizle

            for f in only_in_folder1:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(f))
                self.table.setItem(row, 1, QTableWidgetItem(f"Sadece {os.path.basename(folder1)}"))

            for f in only_in_folder2:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(f))
                self.table.setItem(row, 1, QTableWidgetItem(f"Sadece {os.path.basename(folder2)}"))

            toplam_fark = len(only_in_folder1) + len(only_in_folder2)
            if toplam_fark == 0:
                self.status_bar.showMessage("✅ Hiçbir eksik yok, tamamen eşleşiyor")
            else:
                self.status_bar.showMessage(f"⚠️ Toplam {toplam_fark} farklı kayıt bulundu")

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FolderCompareApp()
    win.show()
    sys.exit(app.exec())
