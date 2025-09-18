import sys
import os
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QStatusBar,
    QGridLayout, QGroupBox, QSpacerItem, QSizePolicy, QToolButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPalette, QGuiApplication


# --- Stil ve Tema Ayarları ---
DARK_STYLESHEET = """
QWidget {
    color: #e0e0e0;
    font-size: 14px;
    background-color: #2c3e50;
}
QMainWindow {
    background-color: #34495e;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #555;
    border-radius: 8px;
    margin-top: 10px;
    background-color: #2c3e50;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #1abc9c;
}
QPushButton, QToolButton {
    background-color: #1abc9c;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
}
QPushButton:hover, QToolButton:hover {
    background-color: #16a085;
}
QPushButton:disabled, QToolButton:disabled {
    background-color: #7f8c8d;
    color: #bdc3c7;
}
QLineEdit, QComboBox, QTableWidget {
    padding: 8px;
    border: 1px solid #555;
    border-radius: 5px;
    background-color: #34495e;
    color: #ecf0f1;
}
QComboBox QAbstractItemView {
    border: 1px solid #555;
    background-color: #34495e;
    color: #ecf0f1;
    selection-background-color: #1abc9c;
    selection-color: #ffffff;
}
QTableWidget {
    gridline-color: #555;
}
QHeaderView::section {
    background-color: #3b5368;
    padding: 8px;
    border: none;
    font-weight: bold;
    color: #ecf0f1;
}
QStatusBar {
    font-size: 12px;
    color: #ecf0f1;
}
"""

LIGHT_STYLESHEET = """
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
QPushButton, QToolButton {
    background-color: #0078d4;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
}
QPushButton:hover, QToolButton:hover {
    background-color: #005a9e;
}
QPushButton:disabled, QToolButton:disabled {
    background-color: #a0a0a0;
}
QLineEdit, QComboBox, QTableWidget {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: #ffffff;
}
QComboBox QAbstractItemView {
    border: 1px solid #dcdcdc;
    background-color: #ffffff;
    color: #333333;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
}
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
"""

def get_icon(name):
    """
    Uygulama içinde kullanılacak ikonları kolayca yüklemek için yardımcı fonksiyon.
    İkonların 'icons' adlı bir alt klasörde olduğunu varsayar.
    Bu fonksiyonu projenize uygun ikon setleri ile daha da geliştirebilirsiniz.
    """
    if os.path.exists(f"icons/{name}.png"):
        return QIcon(f"icons/{name}.png")
    # Alternatif olarak, Qt'nin dahili ikonlarını kullanabilirsiniz.
    # Örnek: return QApplication.style().standardIcon(getattr(QStyle.StandardPixmap, f"SP_{name}"))
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
        self.resize(900, 700)

        self.init_ui()
        self.apply_theme(QGuiApplication.palette().window().color().lightness() < 128) # Sistem temasını algıla


    def init_ui(self):
        """Kullanıcı arayüzünü oluşturur ve düzenler."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tema Değiştirme Butonları
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Tema:")
        theme_layout.addWidget(theme_label)
        
        self.light_theme_btn = QToolButton()
        self.light_theme_btn.setText("☀️ Açık")
        self.light_theme_btn.clicked.connect(lambda: self.apply_theme(False))
        theme_layout.addWidget(self.light_theme_btn)
        
        self.dark_theme_btn = QToolButton()
        self.dark_theme_btn.setText("🌙 Koyu")
        self.dark_theme_btn.clicked.connect(lambda: self.apply_theme(True))
        theme_layout.addWidget(self.dark_theme_btn)
        
        theme_layout.addStretch()
        main_layout.addLayout(theme_layout)

        # Ayarlar Grubu
        settings_group = QGroupBox("Ayarlar")
        settings_layout = QGridLayout()

        settings_layout.addWidget(QLabel("📂 Klasör 1:"), 0, 0)
        self.folder1_edit = QLineEdit()
        self.folder1_edit.setPlaceholderText("Lütfen ilk klasörü seçin...")
        settings_layout.addWidget(self.folder1_edit, 0, 1)
        btn1 = QPushButton(" Seç")
        btn1.clicked.connect(self.select_folder1)
        settings_layout.addWidget(btn1, 0, 2)

        settings_layout.addWidget(QLabel("📁 Klasör 2:"), 1, 0)
        self.folder2_edit = QLineEdit()
        self.folder2_edit.setPlaceholderText("Lütfen ikinci klasörü seçin...")
        settings_layout.addWidget(self.folder2_edit, 1, 1)
        btn2 = QPushButton(" Seç")
        btn2.clicked.connect(self.select_folder2)
        settings_layout.addWidget(btn2, 1, 2)

        settings_layout.addWidget(QLabel("⚙️ Karşılaştırma Tipi:"), 2, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Tam İsim (Uzantısız)", "Sadece Numara", "Sadece Önek"])
        settings_layout.addWidget(self.mode_combo, 2, 1, 1, 2)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # Kontrol Butonları
        control_layout = QHBoxLayout()
        compare_btn = QPushButton("🚀 Karşılaştır")
        compare_btn.clicked.connect(self.compare_folders)
        control_layout.addWidget(compare_btn)

        self.export_btn = QPushButton("💾 Sonuçları Dışa Aktar")
        self.export_btn.clicked.connect(self.export_results)
        self.export_btn.setEnabled(False)
        control_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("🧹 Temizle")
        self.clear_btn.clicked.connect(self.clear_all)
        self.clear_btn.setEnabled(False)
        control_layout.addWidget(self.clear_btn)

        main_layout.addLayout(control_layout)

        # Sonuçlar Grubu
        results_group = QGroupBox("Sonuçlar")
        results_layout = QVBoxLayout()
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Farklı Olan Değer", "Bulunduğu Klasör"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        results_layout.addWidget(self.table)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group, 1) # Tablonun daha fazla yer kaplaması için stretch faktörü

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)


    def apply_theme(self, is_dark):
        """Uygulamaya açık veya koyu temayı uygular."""
        if is_dark:
            self.setStyleSheet(DARK_STYLESHEET)
            self.light_theme_btn.setEnabled(True)
            self.dark_theme_btn.setEnabled(False)
        else:
            self.setStyleSheet(LIGHT_STYLESHEET)
            self.light_theme_btn.setEnabled(False)
            self.dark_theme_btn.setEnabled(True)


    def select_folder(self, line_edit):
        """Klasör seçme iletişim kutusunu açar ve seçilen yolu QLineEdit'e yazar."""
        folder = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        if folder:
            line_edit.setText(folder)

    def select_folder1(self):
        self.select_folder(self.folder1_edit)

    def select_folder2(self):
        self.select_folder(self.folder2_edit)
        
    def clear_all(self):
        """Arayüzdeki tüm girişleri ve sonuçları temizler."""
        self.folder1_edit.clear()
        self.folder2_edit.clear()
        self.table.setRowCount(0)
        self.status_bar.showMessage("Arayüz temizlendi.", 5000)
        self.export_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)


    def compare_folders(self):
        """Klasörleri seçilen moda göre karşılaştırır ve sonuçları tabloya yazar."""
        folder1 = self.folder1_edit.text()
        folder2 = self.folder2_edit.text()
        mode = self.mode_combo.currentText()

        if not folder1 or not folder2:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen karşılaştırma için iki klasör de seçin!")
            return

        try:
            self.status_bar.showMessage(f"'{os.path.basename(folder1)}' ve '{os.path.basename(folder2)}' klasörleri taranıyor...")
            QApplication.processEvents() # Arayüzün donmasını engelle

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
            self.status_bar.showMessage("Hata: Klasör bulunamadı!", 10000)
        except Exception as e:
            QMessageBox.critical(self, "Beklenmedik Hata", f"Bir hata oluştu: {e}")
            self.status_bar.showMessage(f"Beklenmedik bir hata oluştu: {e}", 10000)

    def populate_table(self, only_in_folder1, only_in_folder2, folder1_name, folder2_name):
        """Sonuçları tabloya doldurur ve durum çubuğunu günceller."""
        self.table.setRowCount(0)
        
        is_dark_theme = self.dark_theme_btn.isEnabled() == False
        color1 = QColor("#5e3d3d") if is_dark_theme else QColor("#fff0f0")
        color2 = QColor("#3d4a5e") if is_dark_theme else QColor("#f0faff")

        for f in only_in_folder1:
            self.add_row(f, f"Sadece -> {folder1_name}", color1)

        for f in only_in_folder2:
            self.add_row(f, f"Sadece -> {folder2_name}", color2)

        total_diff = len(only_in_folder1) + len(only_in_folder2)
        if total_diff == 0:
            self.status_bar.showMessage("✅ Harika! İki klasör de tamamen eşleşiyor.", 10000)
            self.export_btn.setEnabled(False)
            self.clear_btn.setEnabled(False)
        else:
            self.status_bar.showMessage(f"⚠️ Toplam {total_diff} farklı kayıt bulundu.", 10000)
            self.export_btn.setEnabled(True)
            self.clear_btn.setEnabled(True)


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
                    file.write("Deger,Bulundugu Klasor\n")
                    for row in range(self.table.rowCount()):
                        val = self.table.item(row, 0).text()
                        loc = self.table.item(row, 1).text()
                        file.write(f'"{val}","{loc}"\n')
                self.status_bar.showMessage(f"Sonuçlar başarıyla '{os.path.basename(path)}' dosyasına aktarıldı!", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Dışa Aktarma Hatası", f"Dosya kaydedilirken bir hata oluştu:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FolderCompareApp()
    win.show()
    sys.exit(app.exec())