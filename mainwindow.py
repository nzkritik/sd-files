from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton, QFileDialog, QMessageBox, QCheckBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from folderpairdialog import FolderPairDialog
from folderpair import FolderPair
from inifilemanager import IniFileManager
import os


class CopyThread(QThread):
     progress_updated = pyqtSignal(int)

     def __init__(self, folder_pairs):
         super().__init__()
         self.folder_pairs = folder_pairs

     def run(self):
         total_files = sum(len(pair.get_files()) for pair in self.folder_pairs)
         copied_files = 0
         for pair in self.folder_pairs:
             pair.copy_files()
             copied_files += len(pair.get_files())
             progress = int((copied_files / total_files) * 100)
             self.progress_updated.emit(progress)


class MainWindow(QMainWindow):
     def __init__(self):
         super().__init__()
         self.setWindowTitle("Folder Pair Copier")
         self.resize(800, 600)

         self.folder_pairs = []
         self.progress_bars = []
         self.checkboxes = []

         self.central_widget = QWidget()
         self.setCentralWidget(self.central_widget)

         self.layout = QVBoxLayout()
         self.central_widget.setLayout(self.layout)

         self.progress_label = QLabel("Overall Progress:")
         self.layout.addWidget(self.progress_label)

         self.overall_progress_bar = QProgressBar()
         self.overall_progress_bar.setTextVisible(True)
         self.layout.addWidget(self.overall_progress_bar)

         self.folder_pairs_layout = QVBoxLayout()
         self.layout.addLayout(self.folder_pairs_layout)

         self.heading_layout = QHBoxLayout()
         self.name_heading_label = QLabel("Name")
         self.copy_heading_label = QLabel("Copy")
         self.edit_heading_label = QLabel("Edit Folder Pair")
         self.delete_heading_label = QLabel("Delete Folder Pair")
         self.heading_layout.addWidget(self.name_heading_label)
         self.heading_layout.addWidget(self.copy_heading_label)
         self.heading_layout.addWidget(self.edit_heading_label)
         self.heading_layout.addWidget(self.delete_heading_label)
         self.folder_pairs_layout.addLayout(self.heading_layout)

         self.add_folder_pair_button = QPushButton("Add Folder Pair")
         self.add_folder_pair_button.clicked.connect(self.add_folder_pair_dialog)
         self.layout.addWidget(self.add_folder_pair_button)

         self.bulk_copy_button = QPushButton("Bulk Copy")
         self.bulk_copy_button.clicked.connect(self.bulk_copy_files)
         self.layout.addWidget(self.bulk_copy_button)

         script_dir = os.path.dirname(os.path.abspath(__file__))
         ini_file_path = os.path.join(script_dir, "folder_pairs.ini")
         self.ini_file_manager = IniFileManager(ini_file_path)
         self.load_folder_pairs()

     def add_folder_pair_dialog(self):
         dialog = FolderPairDialog(self)
         if dialog.exec_() == FolderPairDialog.Accepted:
             name, source, destination = dialog.get_folder_pair()
             folder_pair = FolderPair(name, source, destination)
             self.folder_pairs.append(folder_pair)
             self.add_folder_pair_widget(folder_pair)
             self.save_folder_pairs()

     def add_folder_pair_widget(self, folder_pair):
         folder_pair_widget = QWidget()
         folder_pair_layout = QHBoxLayout()
         folder_pair_widget.setLayout(folder_pair_layout)

         name_label = QLabel(folder_pair.name)
         folder_pair_layout.addWidget(name_label)

         checkbox = QCheckBox()  # Add checkbox widget
         folder_pair_layout.addWidget(checkbox)

         edit_button = QPushButton("Edit")
         edit_button.clicked.connect(lambda: self.edit_folder_pair(folder_pair))
         folder_pair_layout.addWidget(edit_button)

         delete_button = QPushButton("Delete")
         delete_button.clicked.connect(lambda: self.delete_folder_pair(folder_pair))
         folder_pair_layout.addWidget(delete_button)

         self.folder_pairs_layout.addWidget(folder_pair_widget)


     def edit_folder_pair(self, folder_pair):
         dialog = FolderPairDialog(self)
         dialog.set_folder_pair(folder_pair.name, folder_pair.source, folder_pair.destination)
         if dialog.exec_() == FolderPairDialog.Accepted:
             updated_name, updated_source, updated_destination = dialog.get_folder_pair()
             folder_pair.name = updated_name
             folder_pair.source = updated_source
             folder_pair.destination = updated_destination
             # Update the name label
             for widget in self.folder_pairs_layout.children():
                 if isinstance(widget, QWidget):
                     layout = widget.layout()
                     if layout.itemAt(0).widget().text() == folder_pair.name:
                         layout.itemAt(0).widget().setText(folder_pair.name)
             self.save_folder_pairs()  # Save folder pairs after editing a pair

     def delete_folder_pair(self, folder_pair):
         self.folder_pairs.remove(folder_pair)
         # Remove the widget from the layout
         for i in range(self.folder_pairs_layout.count()):
             widget = self.folder_pairs_layout.itemAt(i).widget()
             if widget is not None:
                 layout = widget.layout()
                 if layout.itemAt(0).widget().text() == folder_pair.name:
                     self.folder_pairs_layout.removeItem(layout)
                     break
         self.save_folder_pairs()  # Save folder pairs after deleting a pair

     def bulk_copy_files(self):
         selected_pairs = self.get_selected_folder_pairs()
         if not selected_pairs:
             QMessageBox.warning(self, "No Folder Pairs Selected", "Please select at least one folder pair.")
             return

         self.overall_progress_bar.setValue(0)
         self.overall_progress_bar.setMaximum(100)

         self.copy_thread = CopyThread(selected_pairs)
         self.copy_thread.progress_updated.connect(self.update_progress_bar)
         self.copy_thread.finished.connect(self.copy_thread_finished)
         self.copy_thread.start()

     def update_progress_bar(self, progress):
         self.overall_progress_bar.setValue(progress)

     def copy_thread_finished(self):
         QMessageBox.information(self, "Bulk Copy Finished", "Bulk copying of files has finished.")

     def handle_error(self, error):
         QMessageBox.warning(self, "Error", f"An error occurred: {error}")

     def load_folder_pairs(self):
         if not os.path.isfile(self.ini_file_manager.file_path):
             return

         ini_data = self.ini_file_manager.load_ini_data()
         if "FolderPairs" not in ini_data:
             return

         folder_pairs_data = ini_data["FolderPairs"]
         for pair_key, pair_value in folder_pairs_data.items():
             pair_parts = pair_value.split(",")
             if len(pair_parts) != 3:
                 continue
             name, source, destination = pair_parts
             folder_pair = FolderPair(name, source, destination)
             self.folder_pairs.append(folder_pair)
             self.add_folder_pair_widget(folder_pair)


     def save_folder_pairs(self):
         folder_pairs_data = {}
         for index, folder_pair in enumerate(self.folder_pairs):
             name = folder_pair.name
             source = folder_pair.source
             destination = folder_pair.destination
             pair_value = f"{name},{source},{destination}"
             pair_key = f"pair{index}"
             folder_pairs_data[pair_key] = pair_value

         ini_data = {"FolderPairs": folder_pairs_data}
         self.ini_file_manager.save_ini_data(ini_data)

     def get_selected_folder_pairs(self):
         selected_pairs = []
         for index in range(self.folder_pairs_layout.count()):
             widget = self.folder_pairs_layout.itemAt(index).widget()
             if isinstance(widget, QWidget):
                 layout = widget.layout()
                 name_label = layout.itemAt(0).widget()
                 if isinstance(name_label, QLabel):
                     name = name_label.text()
                     checkbox = layout.itemAt(1).widget()  # Adjusted index to access checkbox
                     if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                         selected_pair = next((pair for pair in self.folder_pairs if pair.name == name), None)
                         if selected_pair is not None:
                             selected_pairs.append(selected_pair)
         return selected_pairs