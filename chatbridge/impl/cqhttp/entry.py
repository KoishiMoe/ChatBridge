import html
import json
import re
from typing import Optional

import websocket

from chatbridge.common.logger import ChatBridgeLogger
from chatbridge.core.client import ChatBridgeClient
from chatbridge.core.network.protocol import ChatPayload, CommandPayload
from chatbridge.impl import utils
from chatbridge.impl.cqhttp.config import CqHttpConfig
from chatbridge.impl.tis.protocol import StatsQueryResult, OnlineQueryResult

ConfigFile = 'ChatBridge_CQHttp.json'
cq_bot: Optional['CQBot'] = None
chatClient: Optional['CqHttpChatBridgeClient'] = None

CQHelpMessage = '''
!!help: 显示本条帮助信息
!!ping: pong!!
!!mc <消息>: 向 MC 中发送聊天信息 <消息>
!!online: 显示在线列表
!!stats <类别> <内容> [<-bot>]: 查询统计信息 <类别>.<内容> 的排名
'''.strip()
StatsHelpMessage = '''
!!stats <类别> <内容> [<-bot>]
添加 `-bot` 来列出 bot
例子:
!!stats used diamond_pickaxe
!!stats custom time_since_rest -bot
'''.strip()


class CQBot(websocket.WebSocketApp):
    def __init__(self, config: CqHttpConfig):
        self.config = config
        websocket.enableTrace(True)
        url = 'ws://{}:{}/'.format(self.config.ws_address, self.config.ws_port)
        if self.config.access_token is not None:
            url += '?access_token={}'.format(self.config.access_token)
        self.logger = ChatBridgeLogger('Bot', file_handler=chatClient.logger.file_handler)
        self.logger.info('Connecting to {}'.format(url))
        # noinspection PyTypeChecker
        super().__init__(url, on_message=self.on_message, on_close=self.on_close)

    def start(self):
        self.run_forever()

    def on_message(self, _, message: str):
        try:
            if chatClient is None:
                return
            data = json.loads(message)
            if data.get('post_type') == 'message' and data.get('message_type') == 'group':
                if data['anonymous'] is None and data['group_id'] == self.config.react_group_id:
                    self.logger.info('QQ chat message: {}'.format(data))
                    args = data['raw_message'].split(' ')

                    if len(args) == 1:
                        if args[0] == '!!help':
                            self.logger.info('!!help command triggered')
                            self.send_text(CQHelpMessage)
                            return

                        elif args[0] == '!!ping':
                            self.logger.info('!!ping command triggered')
                            self.send_text('pong!!')
                            return

                        elif args[0] == '!!online':
                            self.logger.info('!!online command triggered')
                            if chatClient.is_online():
                                command = args[0]
                                client = self.config.client_to_query_online
                                self.logger.info('Sending command "{}" to client {}'.format(command, client))
                                chatClient.send_command(client, command)
                            else:
                                self.send_text('ChatBridge 客户端离线')
                            return

                    if len(args) >= 1 and args[0] == '!!stats':
                        self.logger.info('!!stats command triggered')
                        command = '!!stats rank ' + ' '.join(args[1:])
                        if len(args) == 0 or len(args) - int(command.find('-bot') != -1) != 3:
                            self.send_text(StatsHelpMessage)
                            return
                        if chatClient.is_online:
                            client = self.config.client_to_query_stats
                            self.logger.info('Sending command "{}" to client {}'.format(command, client))
                            chatClient.send_command(client, command)
                        else:
                            self.send_text('ChatBridge 客户端离线')
                        return

                    if self.config.qq_to_mc_auto or (len(args) >= 2 and args[0] == '!!mc'):
                        self.logger.info('message forward triggered')
                        sender = data['sender']['card']
                        if len(sender) == 0:
                            sender = data['sender']['nickname']
                        text = html.unescape(data['raw_message']) if self.config.qq_to_mc_auto \
                            else html.unescape(data['raw_message'].split(' ', 1)[1])
                        chatClient.send_chat(text, sender)

        except:
            self.logger.exception('Error in on_message()')

    def on_close(self, *args):
        self.logger.info("Close connection")

    def _send_text(self, text):
        data = {
            "action": "send_group_msg",
            "params": {
                "group_id": self.config.react_group_id,
                "message": text
            }
        }
        self.send(json.dumps(data))

    def send_text(self, text):
        msg = ''
        length = 0
        lines = text.rstrip().splitlines(keepends=True)
        for i in range(len(lines)):
            msg += lines[i]
            length += len(lines[i])
            if i == len(lines) - 1 or length + len(lines[i + 1]) > 500:
                self._send_text(msg)
                msg = ''
                length = 0

    def send_message(self, sender: str, message: str):
        self.send_text('[{}] {}'.format(sender, message))


class CqHttpChatBridgeClient(ChatBridgeClient):
    mc_to_qq_auto: bool = False
    forward_join_message: bool = True

    @classmethod
    def create(cls, config: CqHttpConfig):
        self = cls(config.aes_key, config.client_info, server_address=config.server_address)
        self.mc_to_qq_auto = config.mc_to_qq_auto
        self.forward_join_message = config.forward_join_message
        return self

    def on_chat(self, sender: str, payload: ChatPayload):
        global cq_bot
        if cq_bot is None:
            return
        try:
            if self.mc_to_qq_auto and not payload.message.strip().startswith('!!'):
                if (not self.forward_join_message) \
                        and (re.match(r'.+ joined .+', payload.message.strip())
                             or re.match(r'.+ left .+', payload.message.strip())):
                    return
                self.logger.info('Message forward triggered')
                cq_bot.send_message(sender, payload.formatted_str())
            else:
                try:
                    prefix, message = payload.message.split(' ', 1)
                except:
                    pass
                else:
                    if prefix == '!!qq':
                        self.logger.info('Triggered command, sending message {} to qq'.format(payload.formatted_str()))
                        payload.message = message
                        cq_bot.send_message(sender, payload.formatted_str())
        except:
            self.logger.exception('Error in on_message()')

    def on_command(self, sender: str, payload: CommandPayload):
        if not payload.responded:
            return
        if payload.command.startswith('!!stats '):
            result = StatsQueryResult.deserialize(payload.result)
            if result.success:
                messages = ['====== {} ======'.format(result.stats_name)]
                messages.extend(result.data)
                messages.append('总数：{}'.format(result.total))
                cq_bot.send_text('\n'.join(messages))
            elif result.error_code == 1:
                cq_bot.send_text('统计信息未找到')
            elif result.error_code == 2:
                cq_bot.send_text('StatsHelper 插件未加载')
        elif payload.command == '!!online':
            result = OnlineQueryResult.deserialize(payload.result)
            cq_bot.send_text('====== 玩家列表 ======\n{}'.format('\n'.join(result.data)))


def main():
    global chatClient, cq_bot
    config = utils.load_config(ConfigFile, CqHttpConfig)
    chatClient = CqHttpChatBridgeClient.create(config)
    utils.start_guardian(chatClient)
    print('Starting CQ Bot')
    cq_bot = CQBot(config)
    cq_bot.start()
    print('Bye~')


if __name__ == '__main__':
    main()
