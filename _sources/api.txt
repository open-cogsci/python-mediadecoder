API Reference
=============

Example player
--------------

.. automodule:: play
	:members: VideoPlayer
	:special-members: __init__


Main classes
------------

Decoder
~~~~~~~
This is the main class that retrieves video and audio frames from MoviePy/ffmpeg.
You can supply Decoder with callback functions that handle stream data once it
is available.

.. automodule:: mediadecoder.decoder
	:members:
	:special-members: __init__

Timer
~~~~~

.. automodule:: mediadecoder.timer
	:members:
	:special-members: __init__

Sound renderers
~~~~~~~~~~~~~~~

This module contains objects that handle the audio frames supplied by Decoder.
At the moment, the only ones that are stable are the PyAudioSoundRenderer and
SounddeviceSoundrenderer (which both are bindings to PortAudio.

Pygame
^^^^^^

.. automodule:: mediadecoder.soundrenderers.pygamerenderer
	:members:
	:special-members: __init__

Pyaudio
^^^^^^^

.. automodule:: mediadecoder.soundrenderers.pyaudiorenderer
	:members:
	:special-members: __init__

Sounddevice
^^^^^^^^^^^

.. automodule:: mediadecoder.soundrenderers.sounddevicerenderer
	:members:
	:special-members: __init__
