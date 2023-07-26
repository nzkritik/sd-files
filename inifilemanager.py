import configparser

class IniFileManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_ini_data(self):
        config = configparser.ConfigParser()
        config.read(self.file_path)
        ini_data = {}
        for section in config.sections():
            ini_data[section] = {}
            for option in config.options(section):
                ini_data[section][option] = config.get(section, option)
        return ini_data

    def save_ini_data(self, ini_data):
        config = configparser.ConfigParser()
        for section, options in ini_data.items():
            config[section] = options
        with open(self.file_path, "w") as config_file:
            config.write(config_file)
