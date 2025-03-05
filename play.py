# -*- coding: utf-8 -*-
import os
import sys
import pygame
import time
import argparse
import logging

logger = logging.getLogger(__name__)

from OpenGL.GL import *
import numpy as np

import mediadecoder  # For the state constants
from mediadecoder.decoder import Decoder


class VideoPlayer:
    """This is an example videoplayer that uses pygame+pyopengl to render a video.
    It uses the Decoder object to decode the video- and audiostream frame by frame.
    It shows each videoframe in a window and places the audioframes in a buffer
    (or queue) from which they are fetched by the soundrenderer object.
    """

    def __init__(
        self, dimensions, fullscreen=False, soundrenderer="pyaudio", loop=False
    ):
        """Constructor.

        Parameters
        ----------
        dimensions : tuple (width, height)
                The dimension of the window in which the video should be shown. Aspect
                ratio is maintained.
        fullscreen : bool, optional
                Indicates whether the video should be displayed in fullscreen.
        soundrenderer : {'pyaudio','pygame'}
                Designates which sound backend should render the sound.
        """

        pygame.init()
        (windowWidth, windowHeight) = dimensions
        flags = pygame.DOUBLEBUF | pygame.OPENGL | pygame.HWSURFACE
        self.fullscreen = fullscreen
        if fullscreen:
            flags = flags | pygame.FULLSCREEN
        pygame.display.set_mode((windowWidth, windowHeight), flags)
        self.windowSize = (windowWidth, windowHeight)

        self.soundrenderer = soundrenderer
        self.loop = loop
        self.texUpdated = False

        self.__initGL()

        self.decoder = Decoder(
            videorenderfunc=self.__texUpdate,
        )
        self.texture_locked = False

    def __initGL(self):
        glViewport(0, 0, self.windowSize[0], self.windowSize[1])

        glPushAttrib(GL_ENABLE_BIT)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)

        glDepthFunc(GL_ALWAYS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0.0, self.windowSize[0], self.windowSize[1], 0.0, 0.0, 1.0)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()

        glColor4f(1, 1, 1, 1)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)

    def calc_scaled_res(self, screen_res, image_res):
        """Calculate appropriate texture size.

        Calculate size or required texture so that it will fill the window,
        but retains the movies original aspect ratio.

        Parameters
        ----------
        screen_res : tuple
                Display window size/Resolution
        image_res : tuple
            Image width and height

        Returns
        -------
        tuple
                width and height of image scaled to window/screen
        """
        rs = screen_res[0] / float(screen_res[1])
        ri = image_res[0] / float(image_res[1])

        if rs > ri:
            return (int(image_res[0] * screen_res[1] / image_res[1]), screen_res[1])
        else:
            return (screen_res[0], int(image_res[1] * screen_res[0] / image_res[0]))

    def load_media(self, vidSource):
        """Loads a video.

        Parameters
        ----------
        vidSource : str
                The path to the video file
        """
        if not os.path.exists(vidSource):
            print("File not found: " + vidSource)
            pygame.display.quit()
            pygame.quit()
            sys.exit(1)

        self.decoder.load_media(vidSource)
        self.decoder.loop = self.loop
        pygame.display.set_caption(os.path.split(vidSource)[1])
        self.vidsize = self.decoder.clip.size

        self.destsize = self.calc_scaled_res(self.windowSize, self.vidsize)
        self.vidPos = (
            (self.windowSize[0] - self.destsize[0]) / 2,
            (self.windowSize[1] - self.destsize[1]) / 2,
        )

        self.__textureSetup()

        if self.decoder.audioformat:
            if self.soundrenderer == "pygame":
                from mediadecoder.soundrenderers import SoundrendererPygame

                self.audio = SoundrendererPygame(self.decoder.audioformat)
            elif self.soundrenderer == "pyaudio":
                from mediadecoder.soundrenderers.pyaudiorenderer import (
                    SoundrendererPyAudio,
                )

                self.audio = SoundrendererPyAudio(self.decoder.audioformat)
            elif self.soundrenderer == "sounddevice":
                from mediadecoder.soundrenderers.sounddevicerenderer import (
                    SoundrendererSounddevice,
                )

                self.audio = SoundrendererSounddevice(self.decoder.audioformat)
            self.decoder.set_audiorenderer(self.audio)

    def __textureSetup(self):
        # Setup texture in OpenGL to render video to
        glEnable(GL_TEXTURE_2D)
        glMatrixMode(GL_MODELVIEW)
        self.textureNo = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.textureNo)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        # Fill texture with black to begin with.
        img = np.zeros([self.vidsize[0], self.vidsize[1], 3], dtype=np.uint8)
        img.fill(0)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGB,
            self.vidsize[0],
            self.vidsize[1],
            0,
            GL_RGB,
            GL_UNSIGNED_BYTE,
            img,
        )

        # Create display list which draws to the quad to which the texture is rendered
        (x, y) = self.vidPos
        (w, h) = self.destsize

        x, y = int(x), int(y)
        w, h = int(w), int(h)

        self.frameQuad = glGenLists(1)
        glNewList(self.frameQuad, GL_COMPILE)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3i(x, y, 0)
        glTexCoord2f(1.0, 0.0)
        glVertex3i(x + w, y, 0)
        glTexCoord2f(1.0, 1.0)
        glVertex3i(x + w, y + h, 0)
        glTexCoord2f(0.0, 1.0)
        glVertex3i(x, y + h, 0)
        glEnd()
        glEndList()

        # Clear The Screen And The Depth Buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def __texUpdate(self, frame):
        """Update the texture with the newly supplied frame."""
        # Retrieve buffer from videosink
        if self.texture_locked:
            return
        self.buffer = frame
        self.texUpdated = True

    def __drawFrame(self):
        """Draws a single frame."""
        # Clear The Screen And The Depth Buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glCallList(self.frameQuad)

    def play(self):
        """Starts playback."""
        # Signal player to start video playback
        self.paused = False

        # Start listening for incoming audio frames
        if self.decoder.audioformat:
            self.audio.start()

        self.decoder.play()

        # While video is playing, render frames
        while self.decoder.status in [mediadecoder.PLAYING, mediadecoder.PAUSED]:
            texture_update_time = 0
            if self.texUpdated:
                t1 = time.time()
                # Update texture
                self.texture_locked = True
                glTexSubImage2D(
                    GL_TEXTURE_2D,
                    0,
                    0,
                    0,
                    self.vidsize[0],
                    self.vidsize[1],
                    GL_RGB,
                    GL_UNSIGNED_BYTE,
                    self.buffer,
                )
                self.texture_locked = False
                texture_update_time = int((time.time() - t1) * 1000)
                self.texUpdated = False

            # Draw the texture to the back buffer
            t1 = time.time()
            self.__drawFrame()
            draw_time = (time.time() - t1) * 1000
            # Flip the buffer to show frame to screen
            t1 = time.time()
            pygame.display.flip()
            flip_time = (time.time() - t1) * 1000

            logger.debug(
                "================== Frame {} ========================".format(
                    self.decoder.current_frame_no
                )
            )
            if texture_update_time:
                logger.debug("Texture updated in {0} ms".format(texture_update_time))
            logger.debug("Texture drawn in {0} ms".format(draw_time))
            logger.debug("Screen flipped in {0} ms".format(flip_time))
            logger.debug("-----------------------------------------------------")
            logger.debug(
                "Total: {} ms".format(texture_update_time + draw_time + flip_time)
            )

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.stop()
                if e.type == pygame.KEYDOWN:
                    # Quitting
                    if e.key == pygame.K_ESCAPE:
                        self.stop()
                    # Pausing
                    elif e.key == pygame.K_SPACE:
                        self.pause()
                    # Seeking
                    elif e.key == pygame.K_RIGHT:
                        new_time = min(
                            self.decoder.current_playtime + 10, self.decoder.duration
                        )
                        self.decoder.seek(new_time)
                    elif e.key == pygame.K_LEFT:
                        new_time = max(self.decoder.current_playtime - 10, 0)
                        self.decoder.seek(new_time)

            pygame.event.pump()  # Prevent freezing of screen while dragging

            # Without this sleep, the video rendering threard goes haywire...
            time.sleep(0.005)

        if self.decoder.audioformat:
            self.audio.close_stream()

        pygame.quit()

    def stop(self):
        """Stops playback."""
        self.decoder.stop()

    def pause(self):
        """Pauses playback."""
        if self.decoder.status == mediadecoder.PAUSED:
            self.decoder.pause()
            self.paused = False
        elif self.decoder.status == mediadecoder.PLAYING:
            self.decoder.pause()
            self.paused = True
        else:
            print("Player not in pausable state")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mediafile", help="the path to the media file to play")
    parser.add_argument(
        "-d", "--debug", help="debugging mode: print lots of info", action="store_true"
    )
    parser.add_argument(
        "-f",
        "--fullscreen",
        help="show movie in fullscreen",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-l", "--loop", help="loop the video", action="store_true", default=False
    )
    parser.add_argument(
        "-s",
        "--soundrenderer",
        help="the backend that should  render the sound (default: sounddevice)",
        choices=["pygame", "pyaudio", "sounddevice"],
        default="sounddevice",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        help="The resolution of the video."
        "\nSpecify as <width>x<height> (default: 1024x768)",
        default="1024x768",
    )

    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    resolution = args.resolution.split("x")
    if len(resolution) != 2:
        print("Invalid value specified for resolution: {}".format(args.resolution))
        sys.exit(2)

    windowRes = tuple(map(int, resolution))
    myVideoPlayer = VideoPlayer(
        windowRes,
        fullscreen=args.fullscreen,
        soundrenderer=args.soundrenderer,
        loop=args.loop,
    )
    myVideoPlayer.load_media(args.mediafile)
    logging.debug("Starting video")
    myVideoPlayer.play()
