import sys
import os
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QStatusBar,
    QGridLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QColor


def get_icon(name):
    """
    Uygulama içinde kullanılacak ikonları kolayca yüklemek için yardımcı fonksiyon.
    İkonların 'icons' adlı bir alt klasörde olduğunu varsayar.
    """
    if os.path.exists(f"icons/{name}.png"):
        return QIcon(f"icons/{name}.png")
    return QIcon()


def extract_number(filename):
    """Dosya adındaki ilk sayısal değeri döndürür, yoksa None döner."""
    match = re.search(r"\d+", filename)
    return match.group(0) if match else None


def extract_prefix(filename):
    """Dosya adındaki ilk sayısal değerden önceki metni döndürür."""
    match = re.search(r"\d+", filename)
    if match:
        return filename[:match.start()]
    return filename


def extract_name_no_ext(filename):
    """Dosya adını uzantısız olarak döndürür."""
    return os.path.splitext(filename)[0]


class FolderCompareApp(QMainWindow):
    """
    İki klasörün içeriğini karşılaştıran ve farkları gösteren
    gelişmiş bir masaüstü uygulaması.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Klasör Karşılaştırma Aracı")
        self.setWindowIcon(get_icon("compare"))
        self.resize(850, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        settings_group = QGroupBox("Ayarlar")
        settings_layout = QGridLayout()

        settings_layout.addWidget(QLabel("📂 Klasör 1:"), 0, 0)
        self.folder1_edit = QLineEdit()
        self.folder1_edit.setPlaceholderText("Lütfen ilk klasörü seçin...")
        settings_layout.addWidget(self.folder1_edit, 0, 1)
        btn1 = QPushButton(get_icon("folder-open"), " Seç")
        btn1.clicked.connect(self.select_folder1)
        settings_layout.addWidget(btn1, 0, 2)

        settings_layout.addWidget(QLabel("📁 Klasör 2:"), 1, 0)
        self.folder2_edit = QLineEdit()
        self.folder2_edit.setPlaceholderText("Lütfen ikinci klasörü seçin...")
        settings_layout.addWidget(self.folder2_edit, 1, 1)
        btn2 = QPushButton(get_icon("folder-open"), " Seç")
        btn2.clicked.connect(self.select_folder2)
        settings_layout.addWidget(btn2, 1, 2)

        settings_layout.addWidget(QLabel("⚙️ Karşılaştırma Tipi:"), 2, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Tam İsim (Uzantısız)", "Sadece Numara", "Sadece Önek"])
        settings_layout.addWidget(self.mode_combo, 2, 1, 1, 2)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        control_layout = QHBoxLayout()
        compare_btn = QPushButton(get_icon("search"), " Karşılaştır")
        compare_btn.clicked.connect(self.compare_folders)
        control_layout.addWidget(compare_btn)

        self.export_btn = QPushButton(get_icon("save"), " Sonuçları Dışa Aktar")
        self.export_btn.clicked.connect(self.export_results)
        self.export_btn.setEnabled(False)
        control_layout.addWidget(self.export_btn)
        main_layout.addLayout(control_layout)

        results_group = QGroupBox("Sonuçlar")
        results_layout = QVBoxLayout()
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Farklı Olan Değer", "Bulunduğu Klasör"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        results_layout.addWidget(self.table)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.apply_styles()

    def apply_styles(self):
        """Uygulamaya modern ve okunaklı bir görünüm kazandırmak için QSS uygular."""
        self.setStyleSheet("""
            QWidget {
                color: #333333;
                font-size: 14px;
            }
            QMainWindow {
                background-color: #f0f2f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dcdcdc;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #a0a0a0;
            }
            QLineEdit, QComboBox, QTableWidget {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #ffffff;
            }
            /* ---- YENİ EKLENEN KURAL ---- */
            /* QComboBox'ın açılır listesini (dropdown) stillendir */
            QComboBox QAbstractItemView {
                border: 1px solid #dcdcdc;
                background-color: #ffffff;
                color: #333333;
                selection-background-color: #0078d4; /* Seçili öğe arkaplanı */
                selection-color: #ffffff; /* Seçili öğe metin rengi */
            }
            /* ---- BİTİŞ ---- */
            QTableWidget {
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QStatusBar {
                font-size: 12px;
            }
        """)

    def select_folder(self, line_edit):
        """Klasör seçme iletişim kutusunu açar ve seçilen yolu QLineEdit'e yazar."""
        folder = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        if folder:
            line_edit.setText(folder)

    def select_folder1(self):
        self.select_folder(self.folder1_edit)

    def select_folder2(self):
        self.select_folder(self.folder2_edit)

    def compare_folders(self):
        """Klasörleri seçilen moda göre karşılaştırır ve sonuçları tabloya yazar."""
        folder1 = self.folder1_edit.text()
        folder2 = self.folder2_edit.text()
        mode = self.mode_combo.currentText()

        if not folder1 or not folder2:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen karşılaştırma için iki klasör de seçin!")
            return

        try:
            files1 = os.listdir(folder1)
            files2 = os.listdir(folder2)

            extractor_map = {
                "Tam İsim (Uzantısız)": extract_name_no_ext,
                "Sadece Numara": extract_number,
                "Sadece Önek": extract_prefix
            }
            extractor = extractor_map.get(mode)
            
            set1 = set(filter(None, (extractor(f) for f in files1)))
            set2 = set(filter(None, (extractor(f) for f in files2)))

            only_in_folder1 = sorted(list(set1 - set2))
            only_in_folder2 = sorted(list(set2 - set1))

            self.populate_table(only_in_folder1, only_in_folder2, os.path.basename(folder1), os.path.basename(folder2))

        except FileNotFoundError:
            QMessageBox.critical(self, "Hata", "Seçilen klasörlerden biri bulunamadı. Lütfen yolu kontrol edin.")
        except Exception as e:
            QMessageBox.critical(self, "Beklenmedik Hata", f"Bir hata oluştu: {e}")

    def populate_table(self, only_in_folder1, only_in_folder2, folder1_name, folder2_name):
        """Sonuçları tabloya doldurur ve durum çubuğunu günceller."""
        self.table.setRowCount(0)

        for f in only_in_folder1:
            self.add_row(f, f"Sadece -> {folder1_name}", QColor("#fff0f0"))

        for f in only_in_folder2:
            self.add_row(f, f"Sadece -> {folder2_name}", QColor("#f0faff"))

        total_diff = len(only_in_folder1) + len(only_in_folder2)
        if total_diff == 0:
            self.status_bar.showMessage("✅ Harika! İki klasör de tamamen eşleşiyor.", 10000)
            self.export_btn.setEnabled(False)
        else:
            self.status_bar.showMessage(f"⚠️ Toplam {total_diff} farklı kayıt bulundu.", 10000)
            self.export_btn.setEnabled(True)

    def add_row(self, value, location, color):
        """Tabloya renklendirilmiş bir satır ekler."""
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        
        item_value = QTableWidgetItem(value)
        item_location = QTableWidgetItem(location)
        
        item_value.setBackground(color)
        item_location.setBackground(color)

        self.table.setItem(row_position, 0, item_value)
        self.table.setItem(row_position, 1, item_location)

    def export_results(self):
        """Tablodaki sonuçları CSV veya Metin dosyası olarak dışa aktarır."""
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Bilgi", "Dışa aktarılacak bir sonuç bulunmuyor.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Sonuçları Kaydet", "", "CSV Dosyaları (*.csv);;Metin Dosyaları (*.txt)"
        )

        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as file:
                    file.write("Deger,Eksik Oldugu Klasor\n")
                    for row in range(self.table.rowCount()):
                        val = self.table.item(row, 0).text()
                        loc = self.table.item(row, 1).text()
                        file.write(f'"{val}","{loc}"\n')
                self.status_bar.showMessage("Sonuçlar başarıyla dışa aktarıldı!", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Dışa Aktarma Hatası", f"Dosya kaydedilirken bir hata oluştu:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FolderCompareApp()
    win.show()
    sys.exit(app.exec())