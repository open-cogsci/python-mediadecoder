# Python 3 compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import time
import threading

from mediadecoder.states import *
from moviepy.tools import cvsecs

class Timer(object):
	""" Timer serves as a video clock that is used to determine which frame needs to be
	displayed at a specified time. the clock runs in its own separate thread. 
	Say you have an instance of Timer called ``clock``. The time can be polled by 
	checking 

	>> clock.time 

	and the current frame can be determined by checking 

	>> clock.current_frame. 

	"""

	def __init__(self, fps=None, max_duration=None):
		""" Constructor.

		Parameters
		----------
		fps : float, optional
			The frames per second of the video for which this timer is created.
		max_duration : float, optional
			The maximum time in seconds the timer should run for.
		"""
		self.status = PAUSED
		self.max_duration = max_duration
		self.fps = fps
		self.reset()

	def reset(self):
		""" Reset the clock to 0."""
		self.previous_intervals = []
		self.current_interval_duration = 0.0

	def pause(self):
		""" Pauses the clock to continue running later.
		Saves the duration of the current interval in the previous_intervals 
		list."""
		if self.status == RUNNING:
			self.status = PAUSED
			self.previous_intervals.append(time.time() - self.interval_start)
			self.current_interval_duration = 0.0
		elif self.status == PAUSED:
			self.interval_start = time.time()
			self.status = RUNNING

	def start(self):
		""" Starts the clock from 0. 
		Uses a separate thread to handle the timing functionalities. """
		if not hasattr(self,"thread") or not self.thread.isAlive():
			self.thread = threading.Thread(target=self.__run)
			self.status = RUNNING
			self.reset()
			self.thread.start()
		else:
			print("Clock already running!")

	def __run(self):
		""" Internal function that is run in a separate thread. Do not call 
		directly. """
		self.interval_start = time.time()
		while self.status != STOPPED:
			if self.status == RUNNING:
				self.current_interval_duration = time.time() - self.interval_start

			# If max_duration is set, stop the clock if it is reached
			if self.max_duration and self.time > self.max_duration:
				self.status == STOPPED

			# One refresh per millisecond seems enough
			time.sleep(0.001)

	def stop(self):
		""" Stops the clock and resets the internal timers. """
		self.status = STOPPED
		self.reset()

	@property
	def time(self):
		""" The current time of the clock. """
		return sum(self.previous_intervals) + self.current_interval_duration

	@time.setter
	def time(self, value):
		""" Sets the time of the clock. Useful for seeking. 
		
		Parameters
		----------
		value : str or int
			The time to seek to. Can be any of the following formats:

		    >>> 15.4 -> 15.4 # seconds
		    >>> (1,21.5) -> 81.5 # (min,sec)
		    >>> (1,1,2) -> 3662 # (hr, min, sec)
		    >>> '01:01:33.5' -> 3693.5  #(hr,min,sec)
		    >>> '01:01:33.045' -> 3693.045
		    >>> '01:01:33,5' #comma works too
		"""
		seconds = cvsecs(value)
		self.reset()
		self.previous_intervals.append(seconds)

	@property
	def current_frame(self):
		""" The current frame number that should be displayed."""
		if not self.__fps:
			raise RuntimeError("fps not set so current frame number cannot be"
				" calculated")
		else:
			return int(self.__fps * self.time)

	@property
	def frame_interval(self):
		""" The duration of a single frame in seconds. """
		if not self.__fps:
			raise RuntimeError("fps not set so current frame interval cannot be"
				" calculated")
		else:
			return 1.0/self.__fps

	@property
	def fps(self):
		""" Returns the frames per second indication that is currently set. """
		return self.__fps

	@fps.setter
	def fps(self,value):
		""" Sets the frames per second of the current movie the clock is used for.

		Parameters
		----------
		value : float
			The fps value.
		"""
		if not value is None:
			if not type(value) == float:
				raise ValueError("fps needs to be specified as a float")
			if value<1.0:
				raise ValueError("fps needs to be greater than 1.0")
		self.__fps = value

	@property
	def max_duration(self):
		""" Returns the max duration the clock should run for. 
		(Usually the duration of the videoclip) """
		return self.__max_duration

	@max_duration.setter
	def max_duration(self,value):
		""" Sets the value of max duration

		Parameters
		----------
		value : float
			The value for max_duration

		Raises
		------
		TypeError
			If max_duration is not a number.
		ValueError
			If max_duration is smaller than 0.
		"""
		if not value is None:
			if not type(value) in [float, int]:
				raise TypeError("max_duration needs to be specified as a number")
			if value<1.0:
				raise ValueError("max_duration needs to be greater than 1.0")
			value = float(value)
		self.__max_duration = value

	def __repr__(self):
		""" Creates a string representation for the print function."""
		if self.__fps:
			return "Clock [current time: {0}, fps: {1}, current_frame: {2}]".format(
				self.time, self.__fps, self.current_frame)
		else:
			return "Clock [current time: {0}]".format(self.time)