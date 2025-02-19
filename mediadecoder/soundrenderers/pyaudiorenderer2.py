import time
import threading

try:
	# Python 3
	from queue import Queue, Empty
except:
	# Python 2
	from Queue import Queue, Empty

from mediadecoder.soundrenderers._base import SoundRenderer

queue_timeout=0.01

class SoundrendererPyAudio(threading.Thread, SoundRenderer):
	""" Uses pyaudio to play sound """
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
		global pyaudio
		import pyaudio

		# Init thread
		super(SoundrendererPyAudio, self).__init__()

		if not queue is None:
			self.queue = queue

		self.pa = pyaudio.PyAudio()
		self.stream = self.pa.open(
			channels  	= audioformat["nchannels"],
			rate 		= audioformat["fps"],
			#frames_per_buffer = audioformat['buffersize']/2,
			format 	= pyaudio.get_format_from_width(audioformat["nbytes"]),
			output 	= True,
		)

	def run(self):
		""" Initializes the stream. """
		if not hasattr(self, 'queue'):
			raise RuntimeError("Audio queue is not intialized.")

		self.stream.start_stream()
		self.keep_listening = True	
		
		while self.keep_listening:
			try:
				frame = self.queue.get(False, timeout=queue_timeout)
				self.stream.write(frame)
			except Empty:
				continue
			time.sleep(0.01)

		self.stream.stop_stream()
		self.stream.close()
		self.pa.terminate()

	def close_stream(self):
		""" Closes the stream. Performs cleanup. """
		self.keep_listening = False
