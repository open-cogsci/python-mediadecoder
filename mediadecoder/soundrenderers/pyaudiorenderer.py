try:
	# Python 3
	from queue import Queue, Empty
except:
	# Python 2
	from Queue import Queue, Empty

from mediadecoder.soundrenderers._base import SoundRenderer

queue_timeout=0.01

class SoundrendererPyAudio(SoundRenderer):
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

		if not queue is None:
			self.queue = queue

		self.pa = pyaudio.PyAudio()
		self.stream = self.pa.open(
			channels  	= audioformat["nchannels"],
			rate 		= audioformat["fps"],
			frames_per_buffer = audioformat['buffersize'],
			format 	= pyaudio.get_format_from_width(audioformat["nbytes"]),
			output 	= True,
			stream_callback=self.get_frame
		)
		self.keep_listening = True

	def get_frame(self, in_data, frame_count, time_info, status):
		""" Callback function for the pyaudio stream. Don't use directly. """
		while self.keep_listening:
			try:
				frame = self.queue.get(False, timeout=queue_timeout)
				return (frame, pyaudio.paContinue)
			except Empty:
				pass
		return (None, pyaudio.paComplete)

	def start(self):
		""" Initializes the stream. """
		if not hasattr(self, 'queue'):
			raise RuntimeError("Audio queue is not intialized.")
		self.stream.start_stream()

	def close_stream(self):
		""" Closes the stream. Performs cleanup. """
		self.keep_listening = False
		self.stream.stop_stream()
		self.stream.close()
		self.pa.terminate()