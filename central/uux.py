"""central.uux: Universal User Experience.

A simple standardized set of functions for user output and input.

Aim is to provide a standard set of tools to display warnings, errors,
info messages, debug messages, error handling
and just about anything else related to non-task output
"""
import time
import os.path
import traceback
import bs4

from colorama import Fore, Back, Style, init
init()

from . import net
from . import env

UUXDEBUG = True
"""Print debug messages."""

UUXINFO = True
""" Print info messages."""

def show_info(message: str, end="\n") -> None:
	""" Print an info message. """
	if UUXINFO:
		print(Fore.LIGHTCYAN_EX + str(message) + Style.RESET_ALL, end=end)

def show_received(sender: str, message: str) -> None:
	""" Shows a message received from a sender"""
	show_debug(sender + " <: " + message + Style.RESET_ALL)

def show_received_highlighted(sender: str, message: str) -> None:
	""" Shows a received message highlighted"""
	print(Fore.LIGHTMAGENTA_EX + sender + " <: " + message + Style.RESET_ALL)

def show_sent(destination: str, message: str) -> None:
	""" Shows a message sent to a destination"""
	print(Fore.LIGHTCYAN_EX + destination + " :> " + Fore.LIGHTWHITE_EX + message)

def show_warning(message: str, end="\n") -> None:
	""" Print a warning (Non-fatal) message. """
	print(Fore.LIGHTYELLOW_EX + "? " + str(message) + Style.RESET_ALL, end=end)

def show_success(message: str, end="\n") -> None:
	""" Prints a success message """
	print(Fore.LIGHTGREEN_EX + str(message) + Style.RESET_ALL, end=end)

def show_error(message: str, end="\n") -> None:
	""" Print a error (Fatal) message. """
	print(Fore.LIGHTRED_EX + "! " + str(message) + Style.RESET_ALL, end=end)

def show_fatal_error(message: str) -> None:
	""" Print a error (Fatal) message, and following stacktrace. """
	show_error(message)
	show_stack_trace()

def show_stack_trace() -> None:
	""" Print a stack trace. """
	print("\n" + Fore.LIGHTBLACK_EX + "--" * 20 + Fore.RED)
	traceback.print_exc()
	print(Fore.LIGHTBLACK_EX + "--" * 20 + "\n" + Style.RESET_ALL)

def show_section() -> None:
	""" Print a section divider. """
	print("\n" + Fore.LIGHTBLACK_EX + "--" * 20 + Style.RESET_ALL)

def show_debug(message: str, end="\n") -> None:
	""" Print a debug (low importance) message """
	if UUXDEBUG:
		print(Fore.LIGHTBLACK_EX + str(message), end=end)

def get_input(prompt: str) -> str:
	""" Get textual from the user. """
	print(Fore.LIGHTMAGENTA_EX + prompt + " <: ", end="")
	try:
		inp = input()
	except (KeyboardInterrupt, EOFError):
		return None
	return inp

def show_fix(fixes: list) -> None:
	""" Shows possbible fixes to the user. """
	print(Fore.LIGHTYELLOW_EX + "! Possible fixes: ")
	for fix in fixes:
		print(Fore.LIGHTYELLOW_EX + "  > " + fix)

def show_colours() -> None:
	"""Shows all possible colours to the user. """

	print(Fore.BLACK   + "Black   " + Fore.LIGHTBLACK_EX   + "Light Black")
	print(Fore.BLUE    + "Blue    " + Fore.LIGHTBLUE_EX    + "Light Blue")
	print(Fore.CYAN    + "Cyan    " + Fore.LIGHTCYAN_EX    + "Light Cyan")
	print(Fore.GREEN   + "Green   " + Fore.LIGHTGREEN_EX   + "Light Green")
	print(Fore.MAGENTA + "Magenta " + Fore.LIGHTMAGENTA_EX + "Light Magenta")
	print(Fore.RED     + "Red     " + Fore.LIGHTRED_EX     + "Light Red")
	print(Fore.WHITE   + "White   " + Fore.LIGHTWHITE_EX   + "Light White")
	print(Fore.YELLOW  + "Yellow  " + Fore.LIGHTYELLOW_EX  + "Light Yellow")

def get_url() -> str:
	""" Get a validly formatted url from the user. """

	url = None
	while url is None:
		url = net.correct_url(get_input("Enter URL"))

		if url is None:
			show_warning("Invalid url, please try again")

	return url

def get_args_url(argv: list, num: int) -> str:
	"""Gets a valid url from the system arguments, otherwise prompts the user to enter one"""
	url = None
	if len(argv) >= num:
		url = net.correct_url(argv[1])
		if url is None:
			show_warning("'" + argv[1] + "' is an invalid URL")

	if url is None:
		url = get_url()

	return url

def clear_term():
	""" Prints the terminal reset character \\033[2J """
	print("\033[2J")

def get_file_existing() -> str:
	""" Gets a valid and existing file from the user """
	while True:
		addr = get_input("Enter File")
		if os.path.exists(addr):
			return addr
		show_warning("File Not Found, please try again")

def show_list(title: str, texts: list) -> None:
	""" Shows a list of items with a title"""
	show_info(title + ":")
	for item in texts:
		show_info("  > " + str(item))

def show_list_numbered(title: str, texts: list) -> None:
	""" Shows a list of numbered items with a title"""
	show_info(title + ":")

	for i in range(0, len(texts)):
		item = texts[i]
		show_info(" " + Fore.LIGHTMAGENTA_EX + str(i+1) + Fore.LIGHTCYAN_EX + "> " + str(item))

def get_int(prompt: str) -> int:
	""" Gets an integer from the user """
	while True:
		entry = get_input(prompt)

		try:
			return int(entry)
		except ValueError:
			show_warning("'" + entry + "' is an invalid integer")

def get_int_in_range(prompt: str, minimum: int, maximum: int) -> int:
	""" Gets a integer from the user within the defined ranges """
	while True:
		entry = get_int(prompt)

		if entry > maximum:
			show_warning("Number cannot be larger than " + str(maximum))
		elif entry < minimum:
			show_warning("Number cannot be smaller than " + str(minimum))
		else:
			return entry

def select_content(content: list) -> list:
	""" Select a list from the provided lists"""

	if len(content) == 1:
		return 0

	# Expected Content format is:
	# content = ["content 1","Content 2"]

	previews = []

	for con in content:

		preview = con[0:70]
		word = preview.split(" ")

		preview = preview.replace(word[0].replace(":", ""), "")
		preview = preview.split("<<")[0].split(">>")[0]
		preview = preview.replace(":", "")

		previews.append(preview)

	show_list_numbered("Page Content", previews)
	index = get_int_in_range("Select Content", 1, len(previews))
	return index - 1

def display_page(page: list, wrap: int) -> bool:
	"""Displays an interactable listadized page"""
	if wrap == 0:
		wrap = 100
	quote = False
	stop = False
	lineNo = 0

	# Options
	animate = True

	for i in range(0,len(page)):
		text = page[i]
		text = text.replace(".)", ").").replace(".\"", "\".")
		text = text.replace(".]", "].")
		page[i] = text

	# Display option state
	def show_options():
		print(Fore.LIGHTBLACK_EX)
		print("Options[ ", end="")
		print("1: Options | ", end="")
		print("2: " + (Fore.RED,Fore.LIGHTYELLOW_EX)[animate] + "Animate" + Fore.LIGHTBLACK_EX + " | ", end="")
		print("8: Skip | ", end="")
		print("0: Exit", end="")
		print(Fore.LIGHTBLACK_EX + " ]" + Fore.RESET+"\n")


	show_options()
	for line in page:
		caret = 0

		for character in line:
			print((Fore.RESET,Fore.LIGHTGREEN_EX)[quote], end="")

			sleepTime = (0, 0.02)[animate]

			time.sleep(sleepTime)

			if character == ".":

				print(". ", end="")
				caret = 0
				lineNo+=1

				while True:
					ch = env.get_char()

					if ch == "8":
						show_warning("SKIPPED")
						print(Fore.RESET)
						return True

					elif ch == "0":
						show_error("EXIT")
						print(Fore.RESET)
						return False

					elif ch == "2":
						animate = not animate
						show_options()

					elif ch == "1":
						show_options()

					else:
						break

				if lineNo > 20:
					clear_term()
					lineNo = 0

			elif character == "…":
				for i in range(0, 3):
					print(".", end="")
					time.sleep(sleepTime/2)
			else:
				print(character, end="")

			caret += 1

			if (caret > wrap and len(line) > (wrap + (wrap / 5))) and character == " ":
				print()
				print("  ", end="")
				caret = 0
				lineNo+=1

		quote = not quote
		env.pause()
		if lineNo > 10:
			clear_term()
			lineNo = 0

	return True
