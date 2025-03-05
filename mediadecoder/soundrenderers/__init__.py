import warnings

try:
    from .pyaudiorenderer import SoundrendererPyAudio
except Exception as e:
    warnings.warn("Could not import pyaudio sound renderer: {}".format(e))

try:
    from .pygamerenderer import SoundrendererPygame
except Exception as e:
    warnings.warn("Could not import pygame sound renderer: {}".format(e))

try:
    from .sounddevicerenderer import SoundrendererSounddevice
except Exception as e:
    warnings.warn("Could not import sounddevice sound renderer: {}".format(e))

__all__ = ["SoundrendererPygame", "SoundrendererPyAudio", "SoundrendererSounddevice"]
