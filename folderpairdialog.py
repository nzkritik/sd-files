from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog

class FolderPairDialog(QDialog):
     def __init__(self, parent=None):
         super().__init__(parent)
         self.setWindowTitle("Add/Edit Folder Pair")
         self.setModal(True)

         self.name_label = QLabel("Name:")
         self.name_line_edit = QLineEdit()
         self.source_label = QLabel("Source:")
         self.source_line_edit = QLineEdit()
         self.source_button = QPushButton("Browse")
         self.destination_label = QLabel("Destination:")
         self.destination_line_edit = QLineEdit()
         self.destination_button = QPushButton("Browse")
         self.save_button = QPushButton("Save")
         self.cancel_button = QPushButton("Cancel")

         layout = QVBoxLayout()
         layout.addWidget(self.name_label)
         layout.addWidget(self.name_line_edit)

         source_layout = QHBoxLayout()
         source_layout.addWidget(self.source_line_edit)
         source_layout.addWidget(self.source_button)
         layout.addWidget(self.source_label)
         layout.addLayout(source_layout)

         destination_layout = QHBoxLayout()
         destination_layout.addWidget(self.destination_line_edit)
         destination_layout.addWidget(self.destination_button)
         layout.addWidget(self.destination_label)
         layout.addLayout(destination_layout)

         layout.addWidget(self.save_button)
         layout.addWidget(self.cancel_button)
         self.setLayout(layout)

         self.save_button.clicked.connect(self.accept)
         self.cancel_button.clicked.connect(self.reject)
         self.source_button.clicked.connect(self.browse_source_folder)
         self.destination_button.clicked.connect(self.browse_destination_folder)

     def set_folder_pair(self, name, source, destination):
         self.name_line_edit.setText(name)
         self.source_line_edit.setText(source)
         self.destination_line_edit.setText(destination)

     def get_folder_pair(self):
         name = self.name_line_edit.text()
         source = self.source_line_edit.text()
         destination = self.destination_line_edit.text()
         return name, source, destination

     def browse_source_folder(self):
         folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
         if folder:
             self.source_line_edit.setText(folder)

     def browse_destination_folder(self):
         folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
         if folder:
             self.destination_line_edit.setText(folder)