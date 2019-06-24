"""central.dc: Discord Chat Functionality.

A centralized place for creating discord bots
Aim is to provide simple and common functions to deal with discord bots
Also check out behaviours for message responses and scenarios
"""

from . import uux
import discord.client

class StandardClient(discord.Client):
	"""A simple discord user designed to look after, and manage, other users."""

	async def on_ready(self) -> None:
		"""Event: Bot logged in."""
		uux.show_info("Logged into " + self.user.name + " [" + self.user.id + "]")
		uux.show_list("Connected Servers", self.servers)

def mentioned(client: discord.Client, message: discord.Message) -> bool:
	"""Return true if client is mentioned in provided message.
	This includes by name, id or mention.
	"""
	return not (client.user.name.lower() not in message.content.lower()) and (client.user.id not in message.content)

async def log_message(message: discord.Message, highlight=False) -> None:
	"""Log a message to console. Highlight will display the message in a differnet color"""
	(uux.show_received, uux.show_received_highlighted)[highlight](str(message.author), str(message.content))

async def send_message(client: discord.Client, channel: discord.Channel, message:str) -> None:
	"""Send a message to the specified channel."""
	try:
		await client.send_message(channel, message)
		uux.show_sent(str(channel), message)
	except Exception as ex:
		# TODO: find what exceptions will be thrown
		uux.show_warning(ex)
