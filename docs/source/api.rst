API Reference
=============

Example player
--------------

.. automodule:: play
	:members: videoPlayer
	:special-members:


Main classes
------------

Decoder
~~~~~~~
This is the main class that retrieves video and audio frames from MoviePy/ffmpeg.
You can supply Decoder with callback functions that handle stream data once it
is available.

.. automodule:: media_player.decoder
	:members:
	:special-members: __init__

Timer
~~~~~

.. automodule:: media_player.timer
	:members:
	:special-members: __init__

Sound renderers
~~~~~~~~~~~~~~~

This module contains objects that handle the audio frames supplied by Decoder.
At the moment, the only one that is stable is the PyAudioSoundRenderer.

.. automodule:: media_player.sound_renderers
	:members:
	:special-members: __init__


OpenSesame specific classes
---------------------------
These classes are for internal usage when the module is used as a plugin in 
OpenSesame, but they can nonetheless serve as examples that demonstrate how to 
implement rendering for various windowing toolkits (i.e. pygame, pyglet, pyopengl)


Pygame Handler
~~~~~~~~~~~~~~
Serves as a base class for the Legacy and Expyriment handlers.

.. automodule:: media_player.handlers.pygame_handler
	:members:
	:special-members: __init__

OpenGL Handler
~~~~~~~~~~~~~~
Serves as a base class for the Psychopy and Expyriment handlers. These use
pyglet.gl and pyOpenGL respectively, but the API difference between these is marginal.
This permits us to use one base class for both GL implementations.

.. automodule:: media_player.handlers.opengl_renderer
	:members:
	:special-members: __init__

Legacy Handler
~~~~~~~~~~~~~~
Handles rendering and event processing when the legacy backend is used. The
legacy backend only uses pygame.

.. automodule:: media_player.handlers.legacy_handler
	:members:
	:special-members: __init__

Expyriment Handler
~~~~~~~~~~~~~~~~~~
Handles rendering and event processing when the Expyriment backend is used.
The expyriment backend uses pyOpenGL for stimulus presentation, and pygame for
event processing.

.. automodule:: media_player.handlers.expyriment_handler
	:members:
	:special-members: __init__

Psychopy Handler
~~~~~~~~~~~~~~~~
Handles rendering and event processing when the psychopy backend is used. Psychopy
uses `pyglet` for both frame rendering and event processing.

.. automodule:: media_player.handlers.psychopy_handler
	:members:
	:special-members: __init__
