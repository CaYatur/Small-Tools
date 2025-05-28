import os

class FileManager:
    def __init__(self, base_directory):
        self.base_directory = base_directory

    def save_file(self, filename, content):
        file_path = os.path.join(self.base_directory, filename)
        with open(file_path, 'w') as file:
            file.write(content)
        return file_path

    def retrieve_file(self, filename):
        file_path = os.path.join(self.base_directory, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return file.read()
        else:
            raise FileNotFoundError(f"The file {filename} does not exist.")

    def delete_file(self, filename):
        file_path = os.path.join(self.base_directory, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise FileNotFoundError(f"The file {filename} does not exist.")

    def list_files(self):
        return os.listdir(self.base_directory)