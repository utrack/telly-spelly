from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox, 
                            QGroupBox, QFormLayout, QProgressBar, QPushButton,
                            QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
import logging
import keyboard
from PyQt6.QtGui import QKeySequence
from settings import Settings
from recorder import AudioRecorder

logger = logging.getLogger(__name__)

class ShortcutEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Click to set shortcut...")
        self.recording = False
        
    def keyPressEvent(self, event):
        if not self.recording:
            return
            
        modifiers = event.modifiers()
        key = event.key()
        
        if key == Qt.Key.Key_Escape:
            self.recording = False
            return
            
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return
            
        # Create key sequence
        sequence = QKeySequence(modifiers.value | key)
        self.setText(sequence.toString())
        self.recording = False
        self.clearFocus()
        
    def mousePressEvent(self, event):
        self.recording = True
        self.setText("Press shortcut keys...")
        
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.recording = False

class SettingsWindow(QWidget):
    initialization_complete = pyqtSignal()
    shortcuts_changed = pyqtSignal(str, str)  # start_key, stop_key

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telly Spelly Settings")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # Initialize settings
        self.settings = Settings()
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Model settings group
        model_group = QGroupBox("Model Settings")
        model_layout = QFormLayout()
        
        # OpenAI API Key field
        self.api_key_field = QLineEdit()
        self.api_key_field.setEchoMode(QLineEdit.EchoMode.Password)  # Hide the API key
        self.api_key_field.setPlaceholderText("Enter your OpenAI API key")
        current_api_key = self.settings.get('openai_api_key', '')
        self.api_key_field.setText(current_api_key)
        self.api_key_field.editingFinished.connect(self.on_api_key_changed)
        model_layout.addRow("OpenAI API Key:", self.api_key_field)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(Settings.VALID_MODELS)
        current_model = self.settings.get('model', 'whisper-1')
        self.model_combo.setCurrentText(current_model)
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        model_layout.addRow("Whisper Model:", self.model_combo)
        
        self.lang_combo = QComboBox()
        # Add all supported languages
        for code, name in Settings.VALID_LANGUAGES.items():
            self.lang_combo.addItem(name, code)
        current_lang = self.settings.get('language', 'auto')
        # Find and set the current language
        index = self.lang_combo.findData(current_lang)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        model_layout.addRow("Language:", self.lang_combo)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Recording settings group
        recording_group = QGroupBox("Recording Settings")
        recording_layout = QFormLayout()
        
        # Get a reference to the global recorder instance if available
        try:
            from main import recorder as global_recorder
            device_list = global_recorder.get_device_list()
        except (ImportError, AttributeError):
            # Fall back to creating a temporary recorder if needed
            logger.warning("Could not access global recorder, creating temporary instance")
            temp_recorder = AudioRecorder()
            device_list = temp_recorder.get_device_list()
        
        self.device_combo = QComboBox()
        # Add all available input devices
        self.device_combo.addItem("Default Microphone", -1)  # Default option with value -1
        for device in device_list:
            self.device_combo.addItem(device['name'], device['index'])
        
        # Get current mic index from settings
        current_mic = self.settings.get('mic_index', -1)
        
        # Find and set the current device
        index = self.device_combo.findData(current_mic)
        if index >= 0:
            self.device_combo.setCurrentIndex(index)
        else:
            self.device_combo.setCurrentIndex(0)  # Default to first item
            
        self.device_combo.currentIndexChanged.connect(self.on_device_changed)
        recording_layout.addRow("Input Device:", self.device_combo)
        
        recording_group.setLayout(recording_layout)
        layout.addWidget(recording_group)
        
        # Loading progress
        self.progress_group = QGroupBox("Model Loading")
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Select a model to load")
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        self.progress_group.setLayout(progress_layout)
        layout.addWidget(self.progress_group)
        
        # Add shortcuts group
        shortcuts_group = QGroupBox("Keyboard Shortcuts")
        shortcuts_layout = QFormLayout()
        
        self.start_shortcut = ShortcutEdit()
        self.start_shortcut.setText(self.settings.get('start_shortcut', 'ctrl+alt+r'))
        self.stop_shortcut = ShortcutEdit()
        self.stop_shortcut.setText(self.settings.get('stop_shortcut', 'ctrl+alt+s'))
        
        shortcuts_layout.addRow("Start Recording:", self.start_shortcut)
        shortcuts_layout.addRow("Stop Recording:", self.stop_shortcut)
        
        apply_btn = QPushButton("Apply Shortcuts")
        apply_btn.clicked.connect(self.apply_shortcuts)
        shortcuts_layout.addRow(apply_btn)
        
        shortcuts_group.setLayout(shortcuts_layout)
        layout.addWidget(shortcuts_group)
        
        # Add stretch to keep widgets at the top
        layout.addStretch()
        
        # Set a reasonable size
        self.setMinimumWidth(300)
        
        # Initialize whisper model
        self.whisper_model = None
        self.current_model = None

    def on_api_key_changed(self):
        api_key = self.api_key_field.text().strip()
        try:
            self.settings.set('openai_api_key', api_key)
            if api_key:
                QMessageBox.information(self, "API Key Saved", "OpenAI API key has been saved. Restart transcription for changes to take effect.")
        except ValueError as e:
            logger.error(f"Failed to set API key: {e}")
            QMessageBox.warning(self, "Error", str(e))
            
    def on_language_changed(self, index):
        language_code = self.lang_combo.currentData()
        try:
            self.settings.set('language', language_code)
        except ValueError as e:
            logger.error(f"Failed to set language: {e}")
            QMessageBox.warning(self, "Error", str(e))

    def on_device_changed(self, index):
        try:
            # Get the device index from the combo box data
            device_index = self.device_combo.currentData()
            self.settings.set('mic_index', device_index)
            logger.info(f"Microphone set to device index: {device_index}")
        except ValueError as e:
            logger.error(f"Failed to set microphone: {e}")
            QMessageBox.warning(self, "Error", str(e))

    def on_model_changed(self, model_name):
        if model_name == self.current_model:
            return
            
        try:
            self.settings.set('model', model_name)
        except ValueError as e:
            logger.error(f"Failed to set model: {e}")
            QMessageBox.warning(self, "Error", str(e))
            return

        self.progress_label.setText(f"Loading {model_name} model...")
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Load model in a separate thread to prevent UI freezing
        QTimer.singleShot(100, lambda: self.load_model(model_name))

    def load_model(self, model_name):
        try:
            # For OpenAI API, we don't need to load a model locally
            # Just update the UI to show it's ready
            self.current_model = model_name
            self.progress_label.setText(f"Using OpenAI Whisper API with model {model_name}")
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
            self.initialization_complete.emit()
        except Exception as e:
            logger.exception("Failed to set up OpenAI client")
            self.progress_label.setText(f"Failed to set up OpenAI client: {str(e)}")
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)

    def apply_shortcuts(self):
        try:
            start_key = self.start_shortcut.text()
            stop_key = self.stop_shortcut.text()
            
            if not start_key or not stop_key:
                QMessageBox.warning(self, "Invalid Shortcuts", 
                    "Please set both start and stop shortcuts.")
                return
            
            if start_key == stop_key:
                QMessageBox.warning(self, "Invalid Shortcuts", 
                    "Start and stop shortcuts must be different.")
                return
            
            # Save shortcuts to settings
            self.settings.set('start_shortcut', start_key)
            self.settings.set('stop_shortcut', stop_key)
            
            self.shortcuts_changed.emit(start_key, stop_key)
            
        except Exception as e:
            logger.error(f"Error applying shortcuts: {e}")
            QMessageBox.critical(self, "Error", 
                "Failed to apply shortcuts. Please try different combinations.") 