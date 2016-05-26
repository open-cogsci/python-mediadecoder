# constants to indicate player status
UNINITIALIZED = 0	# No video file loaded
READY = 1		# Video file loaded and ready to start
PAUSED = 2		# Playback is paused
PLAYING = 3		# Player is playing
EOS = 4		# End of stream has been reached

# constants to indicate clock status
RUNNING = 5		# Clock is ticking
# Clock uses PAUSED status from player variables above
STOPPED = 6		# Clock has been stopped and is reset

__all__ = ['UNINITIALIZED', 'READY', 'PAUSED', 'PLAYING', 'EOS', 'RUNNING', 
	'STOPPED']