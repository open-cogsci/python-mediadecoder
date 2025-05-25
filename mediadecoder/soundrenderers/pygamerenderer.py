import time
import threading
import warnings


try:
    # Python 3
    from queue import Queue, Empty
except:
    # Python 2
    from Queue import Queue, Empty

from ._base import SoundRenderer

queue_timeout = 0.01


class SoundrendererPygame(threading.Thread, SoundRenderer):
    """Uses pygame.mixer to play sound"""

    def __init__(self, audioformat, queue=None, pygame_buffersize=None,
                 pygame_channel_id=None):
        """Constructor.
        Creates a pygame sound renderer using pygame.mixer.

        Parameters
        ----------
        audioformat : dict
                A dictionary containing the properties of the audiostream
        queue : Queue.queue, optional
                A queue object which serves as a buffer on which the individual
                audio frames are placed by the decoder (default=None).
        pygame_buffersize : int, optional
                The buffersize to be used in the Pygame mixer (default=None).
        pygame_channel_id : int, optional
                The ID of a specific pygame mixer channel to use. If none set,
                an appropriate channel is selected automatically (default=None).

        """
        global pygame
        import pygame

        # Init thread
        super(SoundrendererPygame, self).__init__()

        # warnings.warn("Pygame sound renderer is not working correctly yet. Using the "
        # "pyaudio renderer is recommended for now.")

        if not queue is None:
            self.queue = queue

        fps = audioformat["fps"]
        nchannels = audioformat["nchannels"]
        self._nbytes = nbytes = audioformat["nbytes"]
        if pygame_buffersize:
            buffersize = pygame_buffersize
        else:
            buffersize = audioformat["buffersize"]

        if pygame.mixer.get_init() is None:
            if nbytes in (1, 2):
                fmt = -8 * nbytes
            elif nbytes == 4:
                fmt = 32
            pygame.mixer.init(fps, fmt, nchannels, buffersize)
            self._own_mixer = True
        else:
            self._own_mixer = False

        self._channel_id = pygame_channel_id

    def run(self):
        """Main thread function."""
        global pygame
        import pygame

        import numpy as np

        pygame_mixer_unsigned = pygame.mixer.get_init()[1] > 0

        if not hasattr(self, "queue"):
            raise RuntimeError("Audio queue is not intialized.")

        if self._channel_id is not None:
            channel = pygame.mixer.Channel(self._channel_id)
        else:
            channel = pygame.mixer.find_channel(force=True)

        chunk = None
        first_chunk_played = False
        last_channel_state = None
        last_channel_state_change = None
        self.keep_listening = True
        while self.keep_listening:
            if chunk is None:
                try:
                    frame = self.queue.get(timeout=queue_timeout)

                    # Moviepy only supports 8, 16 and 32 bit signed integer.
                    # Pygame also supports 8 and 16 bit unsigned integer, as
                    # well as 32 bit floating point. In case the Pygame mixer
                    # uses one of those formats, we need to convert each audio
                    # frame to that on the fly.
                    if pygame_mixer_unsigned:  # signed int --> unsigned int
                        if self._nbytes == 1:
                            frame = frame.astype(np.uint8) + 128
                        if self._nbytes == 2:
                            frame = frame.astype(np.uint16) + 32768
                    if self._nbytes == 4:  # signed int --> float
                        frame = (frame.astype(np.float32) /
                                 np.iinfo(np.int32).max)

                    chunk = pygame.sndarray.make_sound(frame)
                except Empty:
                    continue

            if not first_chunk_played:
                channel.play(chunk)
                chunk = None
                first_chunk_played = True
            else:
                playing_sound = channel.get_sound()
                queued_sound = channel.get_queue()
                if not queued_sound:
                    channel.queue(chunk)
                    chunk = None
                else:
                    # Fix Pygame channel getting "stuck" (for some reason)
                    now = time.perf_counter()
                    if last_channel_state != [playing_sound, queued_sound]:
                        last_channel_state = [playing_sound, queued_sound]
                        last_channel_state_change = now
                    elif last_channel_state_change is not None:
                        if now - last_channel_state_change > \
                                2 * chunk.get_length():
                            channel.play(chunk)

            time.sleep(0.005)

        if not channel is None and pygame.mixer.get_init():
            channel.stop()
            if self._own_mixer:
                pygame.mixer.quit()

    def close_stream(self):
        """Cleanup (done by pygame.quit() in main loop)"""
        self.keep_listening = False
