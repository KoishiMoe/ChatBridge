import os
import time

from chatbridge.core.client import ChatBridgeClient
from chatbridge.core.config import ClientConfig
from chatbridge.core.network.protocol import ChatPayload
from chatbridge.impl import utils

ConfigFile = 'ChatBridge_client.json'


class CLIClient(ChatBridgeClient):
	stopped = False

	def _on_stopped(self):
		super()._on_stopped()
		if not self.stopped:
			self.logger.error('Client stopped unexpectedly')
			os._exit(1)  # Warning: this is a dirty hack
			# seems that they think the client should be restarted by the user
			# (on disconnect, the client thread is still alive and the client state is not considered as stopped,
			# so we can't use restart() here)
			# I can change this behavior by modifying many files,
			# but I think let systemd (or other service manager) to fuck it is better
		self.logger.info('Disconnected')

	def start(self):
		self.stopped = False
		super().start()
		while not self._is_connected():
			self.logger.info('Waiting for 10 seconds before reconnecting...')
			time.sleep(10)
			super().start()

	def stop(self):
		self.stopped = True
		super().stop()

	def restart(self):
		self.stopped = False
		super().restart()

	def on_chat(self, sender: str, payload: ChatPayload):
		self.logger.info('New message: [{}] {}'.format(sender, payload.formatted_str()))

	def console_loop(self):
		while True:
			text = input()
			self.logger.info('Processing user input "{}"'.format(text))
			if text == 'start':
				self.start()
			elif text == 'stop':
				self.stop()
				break
			elif text == 'restart':
				self.restart()
			elif text == 'ping':
				self.logger.info('Ping: {}'.format(self.get_ping_text()))
			elif text == 'help':
				self.logger.info('start: start the client')
				self.logger.info('stop: stop the client and quit')
				self.logger.info('restart: restart the client')
				self.logger.info('ping: display ping')
			else:
				self.send_chat(text)


def main():
	config: ClientConfig = utils.load_config(ConfigFile, ClientConfig)
	client = CLIClient.create(config)
	print('AES Key = {}'.format(config.aes_key))
	print('Client Info: name = {}, password = {}'.format(config.name, config.password))
	print('Server address = {}'.format(client.get_server_address()))
	client.start()
	client.console_loop()


if __name__ == '__main__':
	main()
