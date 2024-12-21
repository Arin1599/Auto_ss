import json

class SettingsManager:
    def __init__(self, settings_file="screenshot_settings.json"):
        self.settings_file = settings_file
        self.default_settings = {
            "shortcuts": {
                "take_screenshot": "print_screen",
                "save_pdf": "ctrl+s",
                "exit": "esc"
            },
            "quality": 95,
            "compress": False
        }
        self.settings = self.load_settings()

    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except:
            self.save_settings(self.default_settings)
            return self.default_settings

    def save_settings(self, settings):
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings(self.settings)