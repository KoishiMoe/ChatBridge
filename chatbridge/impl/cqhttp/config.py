from typing import List

from chatbridge.core.config import ClientConfig


class CqHttpConfig(ClientConfig):
	ws_address: str = '127.0.0.1'
	ws_port: int = 6700
	access_token: str = ''
	react_group_id: int = 12345
	client_to_query_stats: str = 'MyClient1'
	client_to_query_online: str = 'MyClient2'
	mc_to_qq_auto: bool = False
	qq_to_mc_auto: bool = False
	forward_join_message: bool = True
	admin: List[int] = []
	qq_list: list[int] = []
	mc_list: list[str] = []
	qq_whitelist: bool = False
	mc_whitelist: bool = False
	limiter: bool = False
	limiter_rate: int = 2
	limiter_capacity: int = 5
