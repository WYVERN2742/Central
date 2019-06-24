"""
central.net: Network functions.
Components to deal with and handle networks, from webpages, requests and parsing.

Aim is to provide an array of common tasks when dealing with web resources,
such as requests, downloads, url correction and more.
"""

import requests
import bs4
from . import uux
from . import parse
from . import files

def get_request(url: str) -> requests.Response:
	"""Request a webpage and return the request. Will return None if the request was invalid."""
	url = str(url)
	uux.show_debug("Downloading '" + url +"'...",end="")

	try:
		response = requests.get(url)
		if response.status_code != 200:
			uux.show_error("\nUnable to download '"+ url+ "': " + str(response.status_code))
		else:
			uux.show_debug("Done!")
			return response
	except requests.exceptions.ConnectionError:
		uux.show_stack_trace()
		uux.show_error("\nFailed to connect to '" + url + "'")

	except requests.exceptions.InvalidURL:
		uux.show_error("\nFailed to parse '" + url + "' as URL")

	return None

def correct_url(url: str) -> str:
	"""Attempt to return a correct url from the provided one. Will return `None` if unable to correct."""
	if url[:4] != "http":
		url = "https://" + url

	url_sections = url.split("/")
	new_url = ""
	for section in url_sections:
		if section is not '':
			new_url += section
			if ":" in section:
				new_url += "/"
			new_url += "/"

	url = new_url[:-1]

	if parse.is_url(url):
		return url

	# Failed
	return None

def normalize_url(url: str) -> str:
	"""Corrects and trims the provided URL."""
	url = correct_url(url)
	url = url.split("#")[0]
	url = url.split("&")[0]
	return url

def get_soup(url: str) -> bs4.BeautifulSoup:
	"""Use the url to request a webpage and create a soup for parsing. Returns None if the url response is invalid."""
	url = normalize_url(url)
	response = get_request(url)
	if response is None:
		return None
	return bs4.BeautifulSoup(response.text, "html.parser")

def get_soup_cached(url: str) -> bs4.BeautifulSoup:
	"""Use the url to request a webpage and create a soup for parsing. Returns None if the url response is invalid.

	Will attempt to retrieve from cache before requesting, and will save
	any new requests to cache
	"""
	url = normalize_url(url)

	response = files.cache_get_hashed(url + "soup")
	if response is None:
		response = get_request(url)
		if response is None:
			return None
		response = response.text
		files.cache_save_hashed(url + "soup", response)
	return bs4.BeautifulSoup(response, "html.parser")


def join_url(url: str, sub_url: str) -> str:
	"""Join a main url and a sub-url together."""
	if sub_url in url:
		return url
	sub_url = sub_url.split("#")[0]
	url = url.split("/")[2] + "/"
	return correct_url(url + sub_url)
