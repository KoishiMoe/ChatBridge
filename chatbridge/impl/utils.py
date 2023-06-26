import json
import os
import time
from threading import Thread
from typing import Type, TypeVar, Callable

from chatbridge.core.client import ChatBridgeClient
from chatbridge.core.config import BasicConfig

T = TypeVar('T', BasicConfig, BasicConfig)


def load_config(config_path: str, config_class: Type[T]) -> T:
	config = config_class.get_default()
	if not os.path.isfile(config_path):
		print('Configure file not found!'.format(config_path))
		with open(config_path, 'w', encoding='utf8') as file:
			json.dump(config.serialize(), file, ensure_ascii=False, indent=4)
		print('Default example configure generated'.format(config_path))
		raise FileNotFoundError(config_path)
	else:
		with open(config_path, encoding='utf8') as file:
			config.update_from(json.load(file))
		with open(config_path, 'w', encoding='utf8') as file:
			json.dump(config.serialize(), file, ensure_ascii=False, indent=4)
		return config


def start_guardian(client: ChatBridgeClient, wait_time: float = 10, loop_condition: Callable[[], bool] = lambda: True) -> Thread:
	def loop():
		first = True
		while loop_condition():
			if not client.is_running():
				client.logger.info('Guardian triggered {}'.format('start' if first else 'restart'))
				client.start()
			first = False
			time.sleep(wait_time)
		client.logger.info('Guardian stopped')

	thread = Thread(name='ChatBridge Guardian', target=loop, daemon=True)
	thread.start()
	return thread

def is_valid_minecraft_username(username: str):
  # A valid minecraft username must be between 3 and 16 characters long
  if len(username) < 3 or len(username) > 16:
    return False
  # A valid minecraft username can only contain alphanumeric characters and underscores
  for char in username:
    if not char.isalnum() and char != "_":
      return False
  # A valid minecraft username cannot start or end with an underscore
  if username[0] == "_" or username[-1] == "_":
    return False
  # If all the conditions are met, the username is valid
  return True
