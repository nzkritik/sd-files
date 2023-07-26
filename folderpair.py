import os
import shutil

class FolderPair:
    def __init__(self, name, source, destination):
        self.name = name
        self.source = source
        self.destination = destination

    def get_files(self):
        return os.listdir(self.source)

    def copy_files(self):
        try:
            os.makedirs(self.destination, exist_ok=True)
            files = self.get_files()
            total_files = len(files)
            copied_files = 0
            for file in files:
                source_path = os.path.join(self.source, file)
                destination_path = os.path.join(self.destination, file)
                if os.path.isfile(destination_path):
                    continue
                shutil.copy2(source_path, destination_path)
                copied_files += 1
                progress = int((copied_files / total_files) * 100)
                # progress_updated.emit(progress)  # Remove this line
        except Exception as e:
            # self.error_occurred.emit(str(e))  # Remove this line
            pass
