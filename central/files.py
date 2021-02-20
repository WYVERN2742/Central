"""central.files: File Functions and Services.

A collection of functions and services that include files, such as caching.
Aim is to provide a standardized way of dealing with files, with central implementations
for common file-based tasks, such as caching, loading, saving, and others.
"""

import os
import pickle
import hashlib
import shutil
import urllib
import pathlib

from . import uux

def md5(string: str) -> str:
	"""Get the md5 hash of the provided string."""
	return str(hashlib.md5(string.encode()).hexdigest())

def cache_find(item: str) -> str:
	"""Return the location of a cached object. Returns `None` when the cached object is not found."""
	item = str(item)
	cache = "Cached/" + item

	if os.path.exists(cache):
		return cache

	return None

def cache_get(item: str) -> object:
	"""Get an object from cache, return `None` if not found."""
	item = str(item)
	cache = cache_find(item)

	# cache_find() will return none if the cache does not exist
	# the returned location is guaranteed to exist, so no point checking again.

	if cache is not None:
		cached = pickle.load(open(cache, "rb"))
		uux.show_debug("Cache hit for " + item)
		return cached

	return None

def cache_create() -> None:
	"""Creates a cache."""
	if not os.path.exists("Cached/"):
		os.mkdir("Cached")
		uux.show_debug("Cache created")

def cache_save(item: str, obj: object) -> None:
	"""Save an object to cache with the provided id."""
	item = str(item)
	cache = "Cached/" + item

	cache_create()

	pickle.dump(obj, open(cache, "wb"))
	uux.show_debug("Cached object to " + cache)

def cache_remove(item: str) -> None:
	"""Remove an object from the cache with the provided id."""
	item = str(item)
	cache = "Cached/" + item

	if os.path.exists(cache):
		delete_file(cache)

def cache_get_hashed(item: str) -> object:
	"""Get an object from cache, using a hashed ID. Returns `None` if the object isn't present."""
	return cache_get(md5(item))

def cache_save_hashed(item: str, obj: object) -> None:
	"""Save an item to cache, using a hashed ID."""
	cache_save(md5(item), obj)

def cache_remove_hashed(item: str) -> None:
	"""Delete an item from the cache, using a hashed ID."""
	cache_remove(md5(item))

def copy_file(file: str, dest: str) -> None:
	"""Copy a file from one location to another."""
	uux.show_debug("Copying " + str(file) + " => " + str(dest))
	shutil.copy2(file, dest)

def mkdir(dest: str) -> None:
	"""Create a directory at the given path. Will raise `OSError` if the directory could not be created."""
	if not os.path.exists(dest):
		uux.show_debug("Creating folder at " + dest)
		try:
			os.mkdir(dest)
		except OSError as ex:
			uux.show_warning("Failed to create directory, " + os.strerror(ex.errno))
			raise OSError

def delete_folder(path: str) -> None:
	"""Delete the provided folder, and everything within."""
	uux.show_info("Deleting " + path)

	if not os.path.exists(path):
		# Path does not exist
		return

	try:
		shutil.rmtree(path, True)
	except OSError as ex:
		uux.show_warning("Failed to delete directory, " + os.strerror(ex.errno))

def delete_file(file: str) -> None:
	"""Delete the provided file."""
	uux.show_info("Deleting " + file)

	if not os.path.exists(file):
		# Files does not exist
		return

	os.remove(file)

def copy_folder(src: str, dest: str) -> None:
	"""Copy one folder to another including files recursively."""
	uux.show_info("Copying folder " + src + " => " + dest)

	if not os.path.exists(src):
		uux.show_error("Unable to copy, '" + src + "' does not exist.")
		return

	mkdir(dest)

	for fn in os.listdir(src):
		if os.path.isfile(src + fn):
			try:
				copy_file(src + fn, dest)
			except IOError as ex:
				uux.show_error("Failed to copy file, " + os.strerror(ex.errno))

def download_file(file_url: str, location: str) -> None:
	"""Download the provided file from a url to local location."""
	if os.path.exists(location):
		uux.show_warning("File exists at " + location + ", overwriting!")

	uux.show_debug("Getting metadata from " + file_url)

	u = urllib.request.urlopen(file_url)

	file_size = int(u.getheader('Content-Length'))

	uux.show_info("Downloading "+ str(file_url) + " -> " +  location + " [" + str(file_size) + "] Bytes")

	with open(location, "wb") as f:
		file_size_dl = 0
		block_sz = 8192

		while True:
			# Repeat until file downloaded
			buffer = u.read(block_sz)

			if not buffer:
				# Buffer is empty
				break

			# Write buffer to file
			file_size_dl += len(buffer)
			f.write(buffer)

			# Show progress
			percentage = round(file_size_dl * 100 / file_size, 2)
			uux.show_debug(location + " (" + f'{percentage:.2f}' + ") [ " + str(file_size_dl) + " / " + str(file_size) + " ]")

	uux.show_info("Download complete")

def download_file_cached(file_url: str, location: str) -> None:
	"""Download the file from the provided url to the location. Uses the cache."""
	item = os.path.basename(location)

	local = cache_find(item)

	if local is None:
		# Cached item doesn't exist
		cache_create()
		download_file(file_url, "Cached/" + item)
		copy_file("Cached/" + item, location)
		return

	# Copy file from cache to location
	uux.show_debug("Cache hit for " + item)
	copy_file(local, location)
