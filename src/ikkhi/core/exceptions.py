"""
Custom domain exceptions for the Ikkhi desktop assistant.
"""

class IkkhiError(Exception):
    """Base exception for all domain-specific errors in Ikkhi."""
    pass

class AudioDeviceError(IkkhiError):
    """Raised when an audio input device cannot be initialized or accessed."""
    pass

class SpeechRecognitionError(IkkhiError):
    """Raised when local speech transcription encounters a fatal pipeline failure."""
    pass

class ActionExecutionError(IkkhiError):
    """Raised when a mapped automation action fails during runtime execution."""
    pass

class ScreenCaptureError(IkkhiError):
    """Raised when the screen indexer fails to query or crop the active window."""
    pass

class ScreenSecurityViolation(ScreenCaptureError):
    """Raised when visual screen capture is blocked to protect sensitive or credential data."""
    pass

class ConfigurationError(IkkhiError):
    """Raised when the application configuration is invalid or missing required parameters."""
    pass

