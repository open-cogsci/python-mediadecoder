import warnings

try:
	from mediadecoder.soundrenderers.pyaudiorenderer import SoundrendererPyAudio
except Exception as e:
	warnings.warn("Could not import pyaudio sound renderer: {}".format(e))

try:
	from mediadecoder.soundrenderers.pygamerenderer import SoundrendererPygame
except Exception as e:
	warnings.warn("Could not import pygame sound renderer: {}".format(e))

try:
	from mediadecoder.soundrenderers.sounddevicerenderer import SoundrendererSounddevice
except Exception as e:
	warnings.warn("Could not import sounddevice sound renderer: {}".format(e))

__all__ = ['SoundrendererPygame', 'SoundrendererPyAudio','SoundrendererSounddevice']

