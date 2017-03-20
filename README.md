# Movie decoder for Python based on MoviePy

This library allows you to decode and render movies in Python. It is based on the (rather excellent) [MoviePy](http://zulko.github.io/moviepy/) module created by Zulko, which offers a convenient Python interface to ffmpeg. This library should hence be able to decode any format that ffmpeg supports. If ffmpeg is not found to be installed, moviepy will download it for you on first use, which may take some time (keep an eye on that terminal/command prompt to see the download progress).

One will have to implement the actual rendering of each frame himself, but you can use the play.py module included in this repository as an example. The `play.py` shows how to play a video using OpenGL+pygame for the video rendering and pyaudio for audio playback (using pygame.mixer is also an option, but that doesn't work smoothly yet).

To see it run right away, you can invoke play.py with the following options:

~~~
usage: play.py [-h] [-d] [-f] [-l] [-s {pygame,pyaudio}] [-r RESOLUTION]
               mediafile

positional arguments:
  mediafile             the path to the media file to play

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           debugging mode: print lots of info
  -f, --fullscreen      show movie in fullscreen
  -l, --loop            loop the video
  -s {pygame,pyaudio}, --soundrenderer {pygame,pyaudio}
                        the backend that should render the sound (default:
                        pyaudio)
  -r RESOLUTION, --resolution RESOLUTION
                        The resolution of the video. Specify as
                        <width>x<height> (default: 1024x768)
~~~

This example player furthermore supports pausing playback (by pressing space), seeking 10s forward or backward (by pressing left or right arrow keys) and can be exited by pressing ESC or clicking the close button.

## Dependencies

This module depends on the following other libraries.

- MoviePy (http://zulko.github.io/moviepy/)
- pyAudio (https://people.csail.mit.edu/hubert/pyaudio/)
- numpy (http://www.numpy.org)

That should be enough to get you started, if you plan to implement your own rendering functions for video and audio. If you also want to be able to view the example provided by `play.py` you further need

- pygame (http://www.pygame.org/)
- pyOpenGL (http://pyopengl.sourceforge.net/)

## TODO's

This module is (and will probably always be) a 'work in progress'. For now

- Implementing volume control functions.
- Find a faster method than glTexSubImage2D to get the frame onto the texture to improve performance of the player (even though it works quite well now, it plays Big Buck Bunny at 1080p @60fps without too many dropped frames, but performance is still far behind to other players such as vlc).
- Get pygame audiorenderer working with the current audioqueue implementation.
- Let the decoder also work for audio-only streams/files.

are on my to-do list, but if you have more suggestions, feel free to open up an issue with a feature request.

## API reference

Further documentation, including an API reference, can be found [here](https://dschreij.github.io/python-mediadecoder).

## License

Like moviepy, this module is licensed under the MIT license:

The MIT License (MIT)
Copyright (c) 2016 Daniel Schreij

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.





