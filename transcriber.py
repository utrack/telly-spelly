from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
import os
import logging
import time
import openai
from settings import Settings
logger = logging.getLogger(__name__)

class TranscriptionWorker(QThread):
    finished = pyqtSignal(str)
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, model, audio_file):
        super().__init__()
        self.model = model
        self.audio_file = audio_file
        
    def run(self):
        try:
            if not os.path.exists(self.audio_file):
                raise FileNotFoundError(f"Audio file not found: {self.audio_file}")
                
            self.progress.emit("Loading audio file...")
            
            # Load and transcribe using OpenAI API
            self.progress.emit("Processing audio with OpenAI Whisper API...")
            
            settings = Settings()
            with open(self.audio_file, "rb") as audio_file:
                # Use the OpenAI client to transcribe the audio
                response = self.model.audio.transcriptions.create(
                    file=audio_file,
                    model=settings.get('model', 'whisper-1'),
                    language=settings.get('language', '')
                )
            
            text = response.text.strip()
            if not text:
                raise ValueError("No text was transcribed")
                
            self.progress.emit("Transcription completed!")
            logger.info(f"Transcribed text: {text[:100]}...")
            self.finished.emit(text)
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            self.error.emit(f"Transcription failed: {str(e)}")
            self.finished.emit("")
        finally:
            # Clean up the temporary file
            try:
                if os.path.exists(self.audio_file):
                    os.remove(self.audio_file)
            except Exception as e:
                logger.error(f"Failed to remove temporary file: {e}")

class WhisperTranscriber(QObject):
    transcription_progress = pyqtSignal(str)
    transcription_finished = pyqtSignal(str)
    transcription_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.worker = None
        self._cleanup_timer = QTimer()
        self._cleanup_timer.timeout.connect(self._cleanup_worker)
        self._cleanup_timer.setSingleShot(True)
        self.load_model()
        
    def load_model(self):
        try:
            settings = Settings()
            api_key = settings.get('openai_api_key', None)
            
            if not api_key:
                logger.warning("OpenAI API key not found in settings. Transcription will not work until a key is provided.")
                # Initialize with empty client to prevent crashes, but transcription won't work
                self.model = None
                return
                
            logger.info("Initializing OpenAI client")
            self.model = openai.OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            # Don't raise the exception, just log it
            # This allows the app to start even if the client can't be initialized
            self.model = None
        
    def _cleanup_worker(self):
        if self.worker:
            if self.worker.isFinished():
                self.worker.deleteLater()
                self.worker = None
                
    def transcribe(self, audio_file):
        """Transcribe audio file using OpenAI Whisper API"""
        try:
            # Check if model is initialized
            if self.model is None:
                error_msg = "OpenAI API key not configured. Please add your API key in Settings."
                logger.error(error_msg)
                self.transcription_error.emit(error_msg)
                return
                
            settings = Settings()
            language = settings.get('language', 'auto')
            
            # Emit progress update
            self.transcription_progress.emit("Processing audio...")
            
            # Run transcription with language setting
            with open(audio_file, "rb") as file:
                response = self.model.audio.transcriptions.create(
                    file=file,
                    model="whisper-1",
                    language=None if language == 'auto' else language
                )
            
            text = response.text.strip()
            if not text:
                raise ValueError("No text was transcribed")
                
            self.transcription_progress.emit("Transcription completed!")
            logger.info(f"Transcribed text: {text[:100]}...")
            self.transcription_finished.emit(text)
            
            # Clean up the temporary file
            try:
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            except Exception as e:
                logger.error(f"Failed to remove temporary file: {e}")
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            self.transcription_error.emit(str(e))

    def transcribe_file(self, audio_file):
        if self.worker and self.worker.isRunning():
            logger.warning("Transcription already in progress")
            return
            
        # Check if model is initialized
        if self.model is None:
            error_msg = "OpenAI API key not configured. Please add your API key in Settings."
            logger.error(error_msg)
            self.transcription_error.emit(error_msg)
            return
            
        # Emit initial progress status before starting worker
        self.transcription_progress.emit("Starting transcription...")
            
        self.worker = TranscriptionWorker(self.model, audio_file)
        self.worker.finished.connect(self.transcription_finished)
        self.worker.progress.connect(self.transcription_progress)
        self.worker.error.connect(self.transcription_error)
        self.worker.finished.connect(lambda: self._cleanup_timer.start(1000))
        self.worker.start() 