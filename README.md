# Telly Spelly for KDE Plasma

A sleek KDE Plasma application that records audio and transcribes it in real-time using OpenAI's Whisper. Created by Guilherme da Silveira.

## Features

- 🎙️ **Easy Recording**: Start/stop recording with a single click in the system tray
- 🔊 **Live Volume Meter**: Visual feedback while recording
- ⚡ **Global Shortcuts**: Configurable keyboard shortcuts for quick recording
- 🎯 **Microphone Selection**: Choose your preferred input device
- 📋 **Instant Clipboard**: Transcribed text is automatically copied to your clipboard
- 🎨 **Native KDE Integration**: Follows your system theme and integrates seamlessly with Plasma

## Installation

1. Clone the repository:
```bash
git clone https://github.com/gbasilveira/telly-spelly.git
cd whisper-recorder
```

2. Run the installer:
```bash
python3 install.py
```

The installer will:
- Install all required dependencies
- Set up the application in your user directory
- Create desktop entries and icons
- Configure the launcher

## Requirements

- Python 3.8 or higher
- KDE Plasma desktop environment
- PortAudio (for audio recording)
- CUDA-capable GPU (optional, for faster transcription)

System packages (Ubuntu/Debian):
```bash
sudo apt install python3-pyaudio portaudio19-dev
```

System packages (Fedora):
```bash
sudo dnf install python3-pyaudio portaudio-devel
```

## Usage

1. Launch "Whisper Recorder" from your application menu or run:
```bash
whisper-recorder
```

2. Click the tray icon or use configured shortcuts to start/stop recording
3. When recording stops, the audio will be automatically transcribed
4. The transcribed text is copied to your clipboard

## Configuration

- Right-click the tray icon and select "Settings"
- Configure:
  - Input device selection
  - Global keyboard shortcuts
  - Whisper model selection
  - Interface preferences

## Uninstallation

To remove the application:
```bash
python3 uninstall.py
```

## Technical Details

- Built with PyQt6 for the GUI
- Uses OpenAI's Whisper for transcription
- Integrates with KDE Plasma using system tray and global shortcuts
- Records audio using PyAudio
- Processes audio with scipy for optimal quality

## Contributing

Contributions are welcome! Feel free to:
- Report issues
- Suggest features
- Submit pull requests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the amazing speech recognition model
- KDE Community for the excellent desktop environment
- All contributors and users of this project

## Author

**Guilherme da Silveira**

---

Made with ❤️ for the KDE Community
