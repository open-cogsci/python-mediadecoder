import time
import threading
import warnings

try:
	# Python 3
	from queue import Queue, Empty
except:
	# Python 2
	from Queue import Queue, Empty

from mediadecoder.soundrenderers._base import SoundRenderer

queue_timeout=0.01

class SoundrendererPygame(threading.Thread, SoundRenderer):
	""" Uses pygame.mixer to play sound """
	def __init__(self, audioformat, queue=None):
		"""Constructor.
		Creates a pygame sound renderer using pygame.mixer.
		
		Parameters
		----------
		audioformat : dict
			A dictionary containing the properties of the audiostream
		queue : Queue.queue
			A queue object which serves as a buffer on which the individual
			audio frames are placed by the decoder.
		"""
		global pygame
		import pygame

		# Init thread
		super(SoundrendererPygame, self).__init__()

		warnings.warn("Pygame sound renderer is not working correctly yet. Using the "
			"pyaudio renderer is recommended for now.")

		if not queue is None:
			self.queue = queue

		fps 		= audioformat["fps"]
		nchannels 	= audioformat["nchannels"]
		nbytes   	= audioformat["nbytes"]
		buffersize  = audioformat["buffersize"]

		pygame.mixer.quit()
		pygame.mixer.init(fps, -8 * nbytes, nchannels, buffersize)

	def run(self):
		""" Main thread function. """
		if not hasattr(self, 'queue'):
			raise RuntimeError("Audio queue is not intialized.")

		chunk = None
		channel = None
		self.keep_listening = True
		while self.keep_listening:
			if chunk is None:
				try:
					frame = self.queue.get(timeout=queue_timeout)
					chunk = pygame.sndarray.make_sound(frame)
				except Empty:
					continue

			if channel is None:
				channel = chunk.play()
			else:
				if not channel.get_queue():	
					channel.queue(chunk)
					chunk = None
			time.sleep(0.005)
		
		if not channel is None and pygame.mixer.get_init():
			channel.stop()
			pygame.mixer.quit()

	def close_stream(self):
		""" Cleanup (done by pygame.quit() in main loop) """
		self.keep_listening = False

