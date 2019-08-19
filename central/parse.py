"""central.parse: Parseing and checking.

A library of data definitions and support for comparing and parsing different types of information.

Aim is to provide a large Library of multiple different data formats,
and support for parsing, checking and formatting these datatypes
"""

import re
import bs4
import errno
from . import uux
from . import net
from . import files
# Data Definitions

## text: Sentence
## https://stackoverflow.com/questions/5553410/regular-expression-match-a-sentence#5553924#
RT_SENTENCE = r"[^.!?\s][^.!?]*(?:[.!?](?!['\"]?\s|$)[^.!?]*)*[.!?]?['\"]?(?=\s|$)"

## text: URL
## http://regexlib.com/REDetails.aspx?regexp_id=765
RT_URL = r"^((((H|h)(T|t)|(F|f))(T|t)(P|p)((S|s)?))\:\/\/)?(www.|[a-zA-Z0-9].)[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,6}(\:[0-9]{1,5})*(\/($|[a-zA-Z0-9\.\,\;\?\'\\\+&amp;%\$#\=~_\-]+))*$"

def is_sentence(text: str) -> bool:
	"""Return true if the provided string matches a sentence."""
	if re.search(RT_SENTENCE, text) is None:
		return False
	return True

def is_url(text: str) -> bool:
	"""Return true if the provided string matches a URL."""
	if re.search(RT_URL, text, flags=re.RegexFlag.MULTILINE) is None:
		return False
	return True

def cleanup_text(text: str) -> str:
	"""Normalize punctuation and clean up text."""
	text = str(text)

	# You never have enough: official unicode quotation marks
	text = text.replace('“', '"').replace('”', '"')
	text = text.replace('„', '"').replace('‟', '"')
	text = text.replace('⹂', '"')
	text = text.replace("‘", "'").replace("’", "'")
	text = text.replace("‚", "'").replace("‛", "'")

	text = text.replace("\n.", ".").replace("...", "…")

	# Add spaces after commas
	text = text.replace(",", ", ").replace(",  ", ", ")

	# Specifically for support with uux.display_page(),
	# move periods into quotation marks
	text = text.replace('".', '."')

	text = " ".join(text.split())
	return text

def get_story_url_content(url:str) -> list:
	"""Get story content from the provided url, or from cache if present."""
	url = net.normalize_url(url)

	content = files.cache_get_hashed(url + "content")

	if content is None:
		content = story_content(net.get_soup_cached(url))
		files.cache_save_hashed(url + "content", content)

	return content

def story_content(soup: bs4.BeautifulSoup) -> list:
	"""Create a formatted document list from the provided soup."""
	text = "Parse error"
	for hr in soup.find_all("hr"):
		hr.replace_with('\n""---------------""\n')

	threadmarks = soup.find_all(attrs={"class": "hasThreadmark"})
	threadmarkheaders = soup.find_all(attrs={"class": "message-cell--threadmark-header"})
	storyText = soup.find_all(attrs={"class" : "storytext"})
	storyContent = soup.find_all(attrs={"class" : "storycontent"})
	chapters = soup.find_all(attrs={"id" : "chapters"})
	messageText = soup.find_all(attrs={"class" : "messageText"})
	postContent = soup.find_all(attrs={"class" : "post-content"})
	entry = soup.find_all(attrs={"class" : "entry"})
	messageBody = soup.find_all(attrs={"class" : "message-body"})

	content = []

	if threadmarkheaders:
		# Threadmark headers are in a separate div above the one containing content
		uux.show_debug("Page has " + str(len(threadmarkheaders)) + " threadmarks headers")
		for header in threadmarkheaders:
			text = cleanup_text(header.parent.find(attrs={"class":"bbWrapper"}).text)
			content.append(text)

	elif threadmarks:
		uux.show_debug("Page has " + str(len(threadmarks)) + " threadmarks")
		for mark in threadmarks:

			text = cleanup_text(mark.text)
			content.append(text)

	elif storyText:
		uux.show_debug("Page uses StoryText")
		text = cleanup_text(storyText[0].text)
		content.append(text)

	elif storyContent:
		uux.show_debug("Page uses storycontent")
		text = cleanup_text(storyContent[0].text)
		content.append(text)

	elif chapters:
		uux.show_debug("Page uses chapters")
		text = cleanup_text("".join(map(str, chapters[0].text)))
		content.append(text)

	elif messageText:
		uux.show_debug("Page uses messagetext, using first post...")
		text = cleanup_text(messageText[0].text)
		content.append(text)

	elif postContent:
		uux.show_debug("Page uses postContent, using first post...")
		text = cleanup_text(postContent[0].text)
		content.append(text)

	elif entry:
		uux.show_debug("Page uses entry, using first post...")
		text = cleanup_text(entry[0].text)
		content.append(text)

	elif messageBody:
		uux.show_debug("Page uses messageBody, using first post...")
		text = cleanup_text(messageBody[0].text)
		content.append(text)

	else:
		uux.show_error("Unable to parse page for content!")
		return None
	return content

def get_next_story(url:str) -> str:
	"""Return the url of the next page in the story."""
	soup = net.get_soup_cached(url)
	NEXT_LINKS = [">>", "»"]

	all_links = soup.find_all("a")
	for link in all_links:
		for test in NEXT_LINKS:
			if test in link.text:
				possible_link = net.normalize_url(net.join_url(url, link.get("href")))
				if possible_link not in url:
					return possible_link
	return None
