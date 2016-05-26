try:
	# Python 3
	from queue import Queue, Empty
except:
	# Python 2
	from Queue import Queue, Empty


class SoundRenderer(object):
	""" Base class for sound renderers. """
	def __init__(self, audioformat, queue=None):
		raise NotImplementedError("This class should be subclassed and not be"
			" instantiated directly.")

	@property
	def queue(self):
		""" The audiobuffer object. It should be a thread-safe queue.Queue
		object. """
		return self._queue

	@queue.setter
	def queue(self, value):
		""" Sets the audioqueue.

		Parameters
		----------
		value : queue.Queue
			The buffer from which audioframes are received.
		"""
		if not isinstance(value, Queue):
			raise TypeError("queue is not a Queue object")
		self._queue = value