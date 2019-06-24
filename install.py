# Installs the central package onto the current computer

import os
import site
from central import uux
from central import files

def main(instDir: str) -> None:
	""" Installs the Central package to the provided directory"""

	if instDir == "":
		uux.show_error("Invalid directory")
	try:
		files.copy_folder("central/", instDir)
	except:
		return

	uux.show_info("Checking installation...")

	if not os.path.exists(instDir + "/__init__.py"):
		uux.show_error("Failed to install, package copy worked, but files are not present?")
		return

	uux.show_success("Installed central to " + instDir)

if __name__ == "__main__":
	uux.show_success("Installing central...")
	for site in site.getsitepackages():
		uux.show_debug(site)
		if "packages" in site:
			instDir = site + "/central"
			instDir = instDir.replace("\\", "/")
			break

	main(instDir)
