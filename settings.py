from PyQt6.QtCore import QSettings

class Settings:
    # OpenAI Whisper API uses a single model type
    VALID_MODELS = ['whisper-1','gpt-4o-transcribe']
    # List of valid language codes for Whisper
    VALID_LANGUAGES = {
        '': 'Auto-detect',
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'nl': 'Dutch',
        'pl': 'Polish',
        'ja': 'Japanese',
        'zh': 'Chinese',
        'ru': 'Russian',
        # Add more languages as needed
    }
    
    def __init__(self):
        self.settings = QSettings('TellySpelly', 'TellySpelly')
        
    def get(self, key, default=None):
        value = self.settings.value(key, default)
        
        # Validate specific settings
        if key == 'model' and value not in self.VALID_MODELS:
            return default
        elif key == 'mic_index':
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        elif key == 'language' and value not in self.VALID_LANGUAGES:
            return 'auto'  # Default to auto-detect
                
        return value
        
    def set(self, key, value):
        # Validate before saving
        if key == 'model' and value not in self.VALID_MODELS:
            raise ValueError(f"Invalid model: {value}")
        elif key == 'mic_index':
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid mic_index: {value}")
        elif key == 'language' and value not in self.VALID_LANGUAGES:
            raise ValueError(f"Invalid language: {value}")
                
        self.settings.setValue(key, value)
        self.settings.sync()