try:
	# Python 3
	from queue import Queue, Empty
except:
	# Python 2
	from Queue import Queue, Empty

from mediadecoder.soundrenderers._base import SoundRenderer

queue_timeout=0.01

class SoundrendererSounddevice(SoundRenderer):
	""" Uses python-sounddevice to play sound """
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

		if not queue is None:
			self.queue = queue

		self.stream = sd.OutputStream(
			channels  	= audioformat["nchannels"],
			samplerate 	= audioformat["fps"],
			dtype = 'int{}'.format(audioformat['nbytes']*8),
			blocksize 	= audioformat["buffersize"],
			callback 	= self.get_frame
		)
		self.keep_listening = True

	def get_frame(self, outdata, frames, timedata, status):
		""" Callback function for the audio stream. Don't use directly. """

		if not self.keep_listening:
			raise sd.CallbackStop
		
		try:
			chunk = self.queue.get_nowait()
			# Check if the chunk contains the expected number of frames
			# The callback function raises a ValueError otherwise.
			if chunk.shape[0] == frames:
				outdata[:] = chunk
			else:
				outdata.fill(0)
		except Empty:
			outdata.fill(0)

	def start(self):
		""" Initializes the stream. """
		if not hasattr(self, 'queue'):
			raise RuntimeError("Audio queue is not intialized.")
		self.stream.start()

	def close_stream(self):
		""" Closes the stream. Performs cleanup. """
		self.keep_listening = False
		self.stream.stop()
		self.stream.close()
