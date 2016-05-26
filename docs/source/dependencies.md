## Dependencies

This module depends on the following other libraries.

- MoviePy (http://zulko.github.io/moviepy/)
- pyAudio (https://people.csail.mit.edu/hubert/pyaudio/)

That should be enough to get you started when you plan to implement your own rendering functions to display the video frames. If you also want to be able to view the example provided by `play.py` you furthermore need

- pygame (http://www.pygame.org/)
- pyOpenGL (http://pyopengl.sourceforge.net/)

When importing as a stand alone, you may get notices that 'psychopy' or 'expyriment' were unable to be imported. Don't mind these messages because they are only relevant for when this module is used with OpenSesame.