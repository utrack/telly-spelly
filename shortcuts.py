from PyQt6.QtCore import QObject, pyqtSignal, Qt, pyqtSlot
from PyQt6.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage
from PyQt6.QtWidgets import QApplication
import logging
import os
import uuid

logger = logging.getLogger(__name__)

# D-Bus constants for single instance application
DBUS_SERVICE_NAME = "org.kde.telly_spelly" 
DBUS_OBJECT_PATH = "/org/kde/telly_spelly/Instance"

# session_bus will be passed in __init__

class GlobalShortcuts(QObject):
    start_recording_triggered = pyqtSignal()
    stop_recording_triggered = pyqtSignal()

    @pyqtSlot(result=bool, name='activateStartRecording')
    def _activateStartRecording(self):
        logger.info("D-Bus: activateStartRecording called from remote instance.")
        self.start_recording_triggered.emit()
        return True

    @pyqtSlot(result=bool, name='activateStopRecording')
    def _activateStopRecording(self):
        logger.info("D-Bus: activateStopRecording called from remote instance.")
        self.stop_recording_triggered.emit()
        return True

    def __init__(self, session_bus):
        super().__init__()
        self.session_bus = session_bus

    def register_shortcuts(self):
        if not self.session_bus.registerObject(DBUS_OBJECT_PATH, self, QDBusConnection.RegisterOption.ExportAllSlots):
            logger.error(f"Failed to register D-Bus object at {DBUS_OBJECT_PATH}: {self.session_bus.lastError().message()}")
        else:
            logger.info(f"D-Bus object registered at {DBUS_OBJECT_PATH}")
        if not self.session_bus.registerService(DBUS_SERVICE_NAME):
            logger.warning(f"D-Bus service '{DBUS_SERVICE_NAME}' is already registered. Another instance is running.")
            QApplication.exit(1)
        logger.info(f"D-Bus service '{DBUS_SERVICE_NAME}' registered successfully.")

        return 0
        
    def destroy_shortcuts(self):
        self.session_bus.unregisterObject(DBUS_OBJECT_PATH)
        self.session_bus.unregisterService(DBUS_SERVICE_NAME)
        logger.info("D-Bus service and object unregistered.")

    def _on_start_triggered(self):
        """Called when start recording shortcut is pressed"""
        logger.info(f"Start recording shortcut triggered ({self.start_action_id})")
        self.start_recording_triggered.emit()
        
    def _on_stop_triggered(self):
        """Called when stop recording shortcut is pressed"""
        logger.info(f"Stop recording shortcut triggered ({self.stop_action_id})")
        self.stop_recording_triggered.emit()
    

    def callExistingInstance(self, action):
        if not self.session_bus.isConnected():
            logger.error("D-Bus session bus not connected. Cannot send command to existing instance.")
        else:
            actual_interface_name = "local.GlobalShortcuts" # Updated based on qdbus output
            interface = QDBusInterface(DBUS_SERVICE_NAME, DBUS_OBJECT_PATH, actual_interface_name, self.session_bus)
            if interface.isValid() and interface.service():
                logger.info("Found existing instance. Sending command via D-Bus.")
                reply = None
                if action == "start_recording":
                    reply = interface.call("activateStartRecording")
                elif action == "stop_recording":
                    reply = interface.call("activateStopRecording")
                
                if reply is not None:
                    if reply.type() == QDBusMessage.MessageType.ErrorMessage:
                        logger.error(f"D-Bus call failed: {reply.errorMessage()}")
                        QApplication.exit(1)
                        return 1
                    else:
                        logger.info("D-Bus command sent successfully to existing instance.")
                        QApplication.exit(0)
                        return 0
                else:
                    logger.warning("D-Bus call to existing instance did not return a reply or timed out. The new instance will exit.")
                    QApplication.exit(1)
                    return 1
            else:
                logger.info("No running instance found to send command. This instance will start and attempt the action.")
        