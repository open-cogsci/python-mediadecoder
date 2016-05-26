import threading
import pygame

import warnings
warnings.warn("Pygame sound renderer is not working correctly yet. Using the "
	"pyaudio renderer is recommended for now.")

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
		super(SoundrendererPygame, self).__init__()

		if pygame is None:
			raise RuntimeError("Pygame sound renderer is not available")

		if not queue is None:
			self.queue = queue

		fps 		= audioformat["fps"]
		nchannels 	= audioformat["nchannels"]
		nbytes   	= audioformat["nbytes"]

		pygame.mixer.quit()
		pygame.mixer.init(fps, -8 * nbytes, nchannels)

	def run(self):
		""" Main thread function. """
		if not hasattr(self, 'queue'):
			raise RuntimeError("Audio queue is not intialized.")

		chunk = None
		self.keep_listening = True
		while self.keep_listening:
			if chunk is None:
				try:
					frame = self.queue.get(timeout=queue_timeout)
					chunk = pygame.sndarray.make_sound(frame)
				except Empty:
					continue

			if not hasattr(self,"channel"):
				self.channel = chunk.play()
			else:
				if not pygame.mixer.get_busy():	
					self.channel.queue(chunk)
					chunk = None

	def close_stream(self):
		""" Cleanup (done by pygame.quit() in main loop) """
		self.keep_listening = False

