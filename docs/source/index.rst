.. Moviepy Media Player documentation master file, created by
   sphinx-quickstart on Tue May 24 13:00:08 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MoviePy Media Player documentation
================================================

This library allows you to play and render movies in Python. It is based on the
(rather excellent) MoviePy_ module created by Zulko, which offers a convenient Python interface to ffmpeg. This library should hence be able to render any media format that ffmpeg supports. If ffmpeg is not found to be installed, moviepy will download it for you on first usage, which may take some time (keep an eye on that terminal/command prompt to track the download progress).

This module is mainly designed to serve as a plugin for the OpenSesame_ experiment builder, but it also works on its own. The ``play.py`` contains an example of how to play a video using OpenGL+pygame for the video rendering and pyaudio for audio playback (using pygame.mixer is also an option, but that doesn't work smoothly yet). You can play a video by calling ``python play.py <path_to_videofile>`` from the command line.

.. toctree::
   :maxdepth: 2
   :glob:

   dependencies
   api

View on Github_

.. _MoviePy: http://zulko.github.io/moviepy/
.. _OpenSesame: http://osdoc.cogsci.nl
.. _Github: https://github.com/dschreij/media_player_mpy
