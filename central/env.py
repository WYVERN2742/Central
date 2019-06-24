"""central.env: Environment Functions.

Environment agnostic environment-implementation-specific functions.
Aim is to implement equal-functionality functions, for multiple environments
that require different implementations depending on the operating environment.
"""
import sys
try:
	import msvcrt
	windows = True
except:
	windows = False

def pause() -> None:
	"""Pauses the application until a user enters a keypress."""
	if windows:
		# Windows
		msvcrt.getwch()
		print()
		return

	# Other Os
	input()

def get_char() -> None:
	"""Get a single character from the user."""
	if windows:
		# Windows
		ch = msvcrt.getwch()
		print()
		return ch

	# Other OS
	ch = input()
	while len(ch) != 1:
		ch = input()
	return ch
