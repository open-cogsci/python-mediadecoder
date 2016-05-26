.. Moviepy Media Player documentation master file, created by
   sphinx-quickstart on Tue May 24 13:00:08 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Media decoder documentation
===========================

This library allows you to decode and render video files (and in the future also
audio files) in Python. It provides an internal clock that determines which 
(video and/or audio) frame needs to be displayed at a specified time, and this frame 
can then (optionally) be passed on to a callback function that takes care of the 
actual rendering of the frame. In short, this library should help you get started 
when you want to implement your own video player and want to have full control over
the way audio and video is rendered.

It is based on the (rather excellent) MoviePy_ module created by Zulko, which offers
a convenient Python interface to ffmpeg. This library should hence be able to 
render any media format that ffmpeg supports. If ffmpeg is not found, moviepy 
will download it for you on first usage, which may take some time 
(so keep an eye on that terminal/command prompt to track the download progress).

This library's main purpose is to decode video and/or audio files and supply the 
user with video and audio frames depending on the playtime of the media stream. 
The user thus has to take care of the rendering of these frames himself (although 
modules for sound rendering are included in the package). 
The ``play.py`` contains an example of how to play a video using OpenGL+pygame for 
the video rendering and pyaudio for audio playback (using pygame.mixer is also an 
option, but that doesn't work smoothly yet). You can play a video by calling 
``python play.py <path_to_videofile>`` from the command line or 
``python play.py -h`` to view all command line options.

.. toctree::
   :maxdepth: 2
   :glob:

   dependencies
   api

View on Github_

.. _MoviePy: http://zulko.github.io/moviepy/
.. _Github: https://github.com/dschreij/python-mediadecoder
