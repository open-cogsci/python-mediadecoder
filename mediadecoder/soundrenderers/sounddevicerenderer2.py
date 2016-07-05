import threading
import logging
logger = logging.getLogger(__name__)

try:
	# Python 3
	from queue import Queue, Empty
except:
	# Python 2
	from Queue import Queue, Empty

from mediadecoder.soundrenderers._base import SoundRenderer

queue_timeout=0.01

class SoundrendererSounddevice(threading.Thread, SoundRenderer):
	""" Uses python-sounddevice to play sound. 

	This is an alternative implementation of sounddevicerenderer, that doesn't use
	the callback functionality of sounddevice's OutputStream. The threading is done by
	python, instead of C (under the hood) by sounddevice. I haven't determined yet
	which method is better, so I am leaving them both in for now. """
	
	def __init__(self, audioformat, queue=None):
		"""Constructor.
		Creates a pyaudio sound renderer.
		
		Parameters
		----------
		audioformat : dict
			A dictionary containing the properties of the audiostream
		queue : Queue.queue
			A queue object which serves as a buffer on which the individual
			audio frames are placed by the decoder.
		"""
		global sd
		import sounddevice as sd

		# Init thread
		super(SoundrendererSounddevice, self).__init__()

		if not queue is None:
			self.queue = queue

		self.stream = sd.OutputStream(
			channels  	= audioformat["nchannels"],
			samplerate 	= audioformat["fps"],
			dtype = 'int{}'.format(audioformat['nbytes']*8),
			blocksize = audioformat["buffersize"],
		)
		

	def run(self):
		""" Initializes the stream. """
		if not hasattr(self, 'queue'):
			raise RuntimeError("Audio queue is not intialized.")
		self.keep_listening = True
		self.stream.start()
		
		while self.keep_listening:
			try:
				chunk = self.queue.get(timeout=queue_timeout)
				underflowed = self.stream.write(chunk)
				if underflowed:
					logger.debug("Buffer underrun")
			except Empty:
				pass

		self.stream.stop()
		self.stream.close()


	def close_stream(self):
		""" Closes the stream. Performs cleanup. """
		self.keep_listening = False
