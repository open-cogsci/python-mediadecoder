# Python 3 compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# MoviePy
try:
	from moviepy.video.io.VideoFileClip import VideoFileClip
	import numpy as np
except ImportError as e:
	print("""Error importing dependencies:
{0}

This module depends on the following packages

- MoviePy
- ImageIO
- Numpy

Please make sure that they are installed.""".format(e))

# Other modules
import os
import time
import threading
import logging
logger = logging.getLogger(__name__)

try:
	# Python 3
	from queue import Queue, Full
except:
	# Python 2
	from Queue import Queue, Full
queue_length = 3

from mediadecoder.states import *
from mediadecoder.timer import Timer
from mediadecoder.soundrenderers._base import SoundRenderer

class Decoder(object):
	""" This class loads a video file that can be played. It can 
	be passed a callback function to which decoded video frames should be passed. 
	"""

	def __init__(self, mediafile=None, videorenderfunc=None, play_audio=True):
		"""
		Constructor.

		Parameters
		----------
		mediafile : str, optional
			The path to the mediafile to be loaded (default: None)
		videorenderfunc : callable (default: None)
			Callback function that takes care of the actual
			Rendering of the videoframe.\
			The specified renderfunc should be able to accept the following
			arguments:
				- frame (numpy.ndarray): the videoframe to be rendered
		play_audio : bool, optional
			Whether audio of the clip should be played.
		"""
		# Create an internal timer
		self.clock = Timer()

		# Load a video file if specified, but allow users to do this later
		# by initializing all variables to None
		if not self.load_media(mediafile, play_audio):
			self.reset()

		# Set callback function if set
		self.set_videoframerender_callback(videorenderfunc)

		# Store instance variables
		self.play_audio = play_audio

	@property
	def frame_interval(self):
		""" Duration in seconds of a single frame. """
		return self.clock.frame_interval

	@property
	def current_frame_no(self):
		""" Current frame_no of video. """
		return self.clock.current_frame

	@property
	def current_videoframe(self):
		""" Representation of current video frame as a numpy array. """
		return self.__current_videoframe

	@property
	def current_playtime(self):
		""" Clocks current runtime in seconds. """
		return self.clock.time

	@property
	def loop(self):
		""" Indicates whether the playback should loop. """
		return self._loop
	
	@loop.setter
	def loop(self, value):
		""" Indicates whether the playback should loop. 

		Parameters
		----------
		value : bool
			True if playback should loop, False if not.

		"""
		if not type(value) == bool:
			raise TypeError("can only be True or False")
		self._loop = value

	def reset(self):
		""" Resets the player and discards loaded data. """
		self.clip = None
		self.loaded_file = None

		self.fps = None
		self.duration = None

		self.status = UNINITIALIZED
		self.clock.reset()

		self.loop_count = 0

	def load_media(self, mediafile, play_audio=True):
		""" Loads a media file to decode. 

		If an audiostream is detected, its parameters will be stored in a
		dictionary in the variable `audioformat`. This contains the fields 

		:nbytes: the number of bytes in the stream (2 is 16-bit sound).
		:nchannels: the channels (2 for stereo, 1 for mono)
		:fps: the frames per sec/sampling rate of the sound (e.g. 44100 KhZ).
		:buffersize: the audioframes per buffer.
		
		If play_audio was set to False, or the video does not have an audiotrack,
		`audioformat` will be None.

		Parameters
		----------
		mediafile : str
			The path to the media file to load.
		play_audio : bool, optional
			Indicates whether the audio of a movie should be played.

		Raises
		------
		IOError
			When the file could not be found or loaded.
		"""
		if not mediafile is None:
			if os.path.isfile(mediafile):
				self.clip = VideoFileClip(mediafile, audio=play_audio)

				self.loaded_file = os.path.split(mediafile)[1]

				## Timing variables
				# Clip duration
				self.duration = self.clip.duration
				self.clock.max_duration = self.clip.duration
				logger.debug("Video clip duration: {}s".format(self.duration))

				# Frames per second of clip
				self.fps = self.clip.fps
				self.clock.fps = self.clip.fps
				logger.debug("Video clip FPS: {}".format(self.fps))

				if play_audio and self.clip.audio:
					buffersize = int(self.frame_interval*self.clip.audio.fps)
					self.audioformat = {
						'nbytes':  	  	2,
						'nchannels':	self.clip.audio.nchannels,
						'fps':	 	  	self.clip.audio.fps,
						'buffersize':	buffersize
					}
					logger.debug("Audio loaded: \n{}".format(self.audioformat))
					logger.debug("Creating audio buffer of length: "
						" {}".format(queue_length))
					self.audioqueue = Queue(queue_length)
				else:
					self.audioformat = None

				logger.debug('Loaded {0}'.format(mediafile))
				self.status = READY
				return True
			else:
				raise IOError("File not found: {0}".format(mediafile))
		return False

	def set_videoframerender_callback(self, func):
		""" Sets the function to call when a new frame is available. 
		This function is passed the frame (in the form of a numpy.ndarray) and
		should take care of the rendering. 

		Parameters
		----------
		func : callable
			The function to pass the new frame to once it becomes available.
		"""

		# Check if renderfunc is indeed a function
		if not func is None and not callable(func):
			raise TypeError("The object passed for videorenderfunc is not a function")
		self.__videorenderfunc = func

	def set_audiorenderer(self, renderer):
		""" Sets the SoundRenderer object. This should take care of processing 
		the audioframes set in audioqueue.

		Parameters
		----------
		renderer : soundrenderers.SoundRenderer
			A subclass of soundrenderers.SoundRenderer that takes care of the
			audio rendering.

		Raises
		------
		RuntimeError
			If no information about the audiostream is available. This could be
			because no video has been loaded yet, or because no embedded 
			audiostream could be detected in the video, or play_sound was set
			to False.
		"""
		if not hasattr(self, 'audioqueue') or self.audioqueue is None:
			raise RuntimeError("No video has been loaded, or no audiostream "
				"was detected.")
		if not isinstance(renderer, SoundRenderer):
			raise TypeError("Invalid renderer object. Not a subclass of "
				"SoundRenderer")
		self.soundrenderer = renderer
		self.soundrenderer.queue = self.audioqueue

	def play(self):
		""" Start the playback of the video. 
		The playback loop is run in a separate thread, so this function returns 
		immediately. This allows one to implement things such as event handling 
		loops (e.g. check for key presses) elsewhere.
		"""
		### First do some status checks

		# Make sure a file is loaded
		if self.status == UNINITIALIZED or self.clip is None:
			raise RuntimeError("Player uninitialized or no file loaded")

		# Check if playback has already finished (rewind needs to be called first)
		if self.status == EOS:
			logger.debug("End of stream has already been reached")
			return

		# Check if playback hasn't already been started (and thus if play()
		# has not been called before from another thread for instance)
		if self.status in [PLAYING,PAUSED]:
			logger.warning("Video already started")
			return

		### If all is in order start the general playing loop
		if self.status == READY:
			self.status = PLAYING

		self.last_frame_no = 0

		if not hasattr(self,"renderloop") or not self.renderloop.isAlive():
			if self.audioformat:
				# Chop the total stream into separate audio chunks that are the
				# lenght of a video frame (this way the index of each chunk 
				# corresponds to the video frame it belongs to.)
				self.__calculate_audio_frames()
				# Start audio handling thread. This thread places audioframes
				# into a sound buffer, untill this buffer is full.
				self.audioframe_handler = threading.Thread(
					target=self.__audiorender_thread)
				self.audioframe_handler.start()

			# Start main rendering loop.
			self.renderloop = threading.Thread(target=self.__render)
			self.renderloop.start()
		else:
			logger.warning("Rendering thread already running!")

	def pause(self):
		""" Pauses or resumes the video and/or audio stream. """

		# Change playback status only if current status is PLAYING or PAUSED 
		# (and not READY).
		logger.debug("Pausing playback")
		if self.status == PAUSED:
			# Recalculate audio stream position to make sure it is not out of
			# sync with the video
			self.__calculate_audio_frames()
			self.status = PLAYING
			self.clock.pause()
		elif self.status == PLAYING:
			self.status = PAUSED
			self.clock.pause()

	def stop(self):
		""" Stops the video stream and resets the clock. """

		logger.debug("Stopping playback")
		# Stop the clock
		self.clock.stop()
		# Set plauyer status to ready
		self.status = READY

	def seek(self, value):
		""" Seek to the specified time.

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
		# Pause the stream
		self.pause()
		# Make sure the movie starts at 1s as 0s gives trouble.
		self.clock.time = max(0.5, value)
		logger.debug("Seeking to {} seconds; frame {}".format(self.clock.time, 
			self.clock.current_frame))
		if self.audioformat:
			self.__calculate_audio_frames()
		# Resume the stream
		self.pause()

	def rewind(self):
		""" Rewinds the video to the beginning.
		Convenience function simply calling seek(0). """
		self.seek(0.5)

	def __calculate_audio_frames(self):
		""" Aligns audio with video. 
		This should be called for instance after a seeking operation or resuming 
		from a pause. """

		if self.audioformat is None:
			return
		start_frame = self.clock.current_frame
		totalsize = int(self.clip.audio.fps*self.clip.audio.duration)
		self.audio_times = list(range(0, totalsize, 
			self.audioformat['buffersize'])) + [totalsize]
		# Remove audio segments up to the starting frame
		del(self.audio_times[0:start_frame])

	def __render(self):
		""" Main render loop. 

		Checks clock if new video and audio frames need to be rendered. 
		If so, it passes the frames to functions that take care 
		of rendering these frames. """

		# Render first frame
		self.__render_videoframe()

		# Start videoclock with start of this thread
		self.clock.start()

		logger.debug("Started rendering loop.")
		# Main rendering loop
		while self.status in [PLAYING,PAUSED]:
			current_frame_no = self.clock.current_frame

			# Check if end of clip has been reached
			if self.clock.time >= self.duration:
				logger.debug("End of stream reached at {}".format(self.clock.time))
				if self.loop:
					logger.debug("Looping: restarting stream")
					# Seek to the start
					self.rewind()
					self.loop_count += 1
				else:
					# End of stream has been reached
					self.status = EOS
					break

			if self.last_frame_no != current_frame_no:
				# A new frame is available. Get it from te stream
				self.__render_videoframe()

			self.last_frame_no = current_frame_no

			# Sleeping is a good idea to give the other threads some breathing
			# space to do their work.
			time.sleep(0.005)

		# Stop the clock.
		self.clock.stop()
		logger.debug("Rendering stopped.")

	def __render_videoframe(self):
		""" Retrieves a new videoframe from the stream.

		Sets the frame as the __current_video_frame and passes it on to
		__videorenderfunc() if it is set. """

		new_videoframe = self.clip.get_frame(self.clock.time)
		# Pass it to the callback function if this is set
		if callable(self.__videorenderfunc):
			self.__videorenderfunc(new_videoframe)
		# Set current_frame to current frame (...)
		self.__current_videoframe = new_videoframe

	def __audiorender_thread(self):
		""" Thread that takes care of the audio rendering. Do not call directly,
		but only as the target of a thread. """
		new_audioframe = None
		logger.debug("Started audio rendering thread.")

		while self.status in [PLAYING,PAUSED]:
			# Retrieve audiochunk
			if self.status == PLAYING:
				if new_audioframe is None:
					# Get a new frame from the audiostream, skip to the next one
					# if the current one gives a problem
					try:
						start = self.audio_times.pop(0)
						stop = self.audio_times[0]
					except IndexError:
						logger.debug("Audio times could not be obtained")
						time.sleep(0.02)
						continue

					# Get the frame numbers to extract from the audio stream.
					chunk = (1.0/self.audioformat['fps'])*np.arange(start, stop)

					try:
						# Extract the frames from the audio stream. Does not always,
						# succeed (e.g. with bad streams missing frames), so make
						# sure this doesn't crash the whole program.
						new_audioframe = self.clip.audio.to_soundarray(
							tt = chunk,
							buffersize = self.frame_interval*self.clip.audio.fps,
							quantize=True
						)
					except OSError as e:
						logger.warning("Sound decoding error: {}".format(e))
						new_audioframe = None
				# Put audioframe in buffer/queue for soundrenderer to pick up. If
				# the queue is full, try again after a timeout (this allows to check
				# if the status is still PLAYING after a pause.)
				if not new_audioframe is None:
					try:
						self.audioqueue.put(new_audioframe, timeout=.05)
						new_audioframe = None
					except Full:
						pass
			
			time.sleep(0.005)
		
		logger.debug("Stopped audio rendering thread.")

	def __repr__(self):
		""" Create a string representation for when print() is called. """
		return "Decoder [file loaded: {0}]".format(self.loaded_file)


