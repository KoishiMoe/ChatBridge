# ChatBridge

> Broadcast chat between Minecraft servers or even discord server

This is a fork of [TIS Union's ChatBridge](https://github.com/TISUnion/ChatBridge), which adds some potentially useful features.

This software is mainly reserved for self-use, so while you can submit an issue or pr, bug-related ones will generally be accepted, while feature-related ones may not.

**Please note that neither I nor TIS Union is responsible for any actions you take with this software and its consequences.**

## Usage

Enter `python ChatBridge.pyz` in command line to see possible helps

At launch, if the configure file is missing, chatbridge will automatically generate a default one and exit

## Requirement

Although all versions of python above 3.6 are theoretically supported, I recommend that you use 3.10 or above, as I won't test it on 3.9 and below

Requirements stored in `requirements.txt`, use `pip install -r requirements.txt` to install

```
mcdreforged>=2.2.0
pycryptodome
colorlog
```

## CLI Server

```
python ChatBridge.pyz server
```

Configure:

```json5
{
    "aes_key": "ThisIstheSecret",  // the common encrypt key for all clients
    "hostname": "localhost",  // the hostname of the server. Set it to "0.0.0.0" for general binding
    "port": 30001,  // the port of the server
    "clients": [  // a list of client
        {
            "name": "MyClientName",  // client name
            "password": "MyClientPassword"  // client password
        }
    ]
}
```

## CLI Client

```
python ChatBridge.pyz client
```

Configure:

```json5
{
    "aes_key": "ThisIstheSecret",  // the common encrypt key
    "name": "MyClientName",  // the name of the client
    "password": "MyClientPassword",  // the password of the client
    "server_hostname": "127.0.0.1",  // the hostname of the server
    "server_port": 30001  // the port of the server
}
```

## [MCDReforged](https://github.com/Fallen-Breath/MCDReforged) plugin client

Required MCDR >=2.2

Just put the `.pyz` file into the plugin folder

Extra configure fields (compared to [CLI client](#cli-client))

```json5
    "debug": false,  // for switching debug logging on
```

## Discord bot client

`python ChatBridge.pyz discord_bot`

Extra requirements (also listed in `/chatbridge/impl/discord/requirements.txt`):

```
discord.py>=2.0.0
```

Extra configure fields (compared to [CLI client](#cli-client))

```json5
    "bot_token": "your.bot.token.here",  // the token of your discord bot
    "channels_for_command": [  // a list of channels, public commands can be used here
        123400000000000000,
        123450000000000000
    ],
    "channel_for_chat": 123400000000000000,  // the channel for chatting and private commands
    "command_prefix": "!!",
    "client_to_query_stats": "MyClient1",  // it should be a client as an MCDR plugin, with stats_helper plugin installed in the MCDR
    "client_to_query_online": "MyClient2"  // a client described in the following section "Client to respond online command"
```

### Commands

`!!stats` will send command to `MyClient1` to query the StatsHelper plugin in the specific client for data

`!!online` will send command to `MyClient2` to use rcon to get `glist` command reply in bungeecord server

## Client as a cqhttp client

```
python ChatBridge.pyz cqhttp_bot
```

Extra requirements (also listed in `/chatbridge/impl/cqhttp/requirements.txt`):

```
websocket>=0.2.1
websocket-client>=1.2.1
```

Needs any cqhttp protocol provider to work. e.g. [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)

Due to lack of channel division in QQ group (not like discord), to prevent message spam, by default player needs to use special command to let the bot recognize the message:

- In MC (othe client) use `!!qq <message>` to send message to QQ
- In QQ use `!!mc <message>` to send message

Type `!!help` in QQ for more help

To execute commands in Minecraft server (you need to be set as admin in the config file):

- `#/ <client name> <command>` to execute a vanilla command
- `#! <client name> <command>` to execute an MCDR command

Specially you can kill a carpet fake player with `!!killbot <client name> <bot name>`. This doesn't require admin privilege

Extra configure fields (compared to [CLI client](#cli-client))

`ws_address`, `ws_port` and `access_token` are the same as the value in the config file of coolq-http-api

```json5
    "ws_address": "127.0.0.1",
    "ws_port": 6700,
    "access_token": "access_token.here",
    "react_group_id": 12345,  // the target QQ group id
    "client_to_query_stats": "MyClient1",  // it should be a client as an MCDR plugin, with stats_helper plugin installed in the MCDR
    "client_to_query_online": "MyClient2",  // a client described in the following section "Client to respond online command"
    "mc_to_qq_auto": false,  // Whether to forward messages in mc to qq automatically (so you don't need to add "!!qq" prefix).
    "qq_to_mc_auto": false,  // Whether to forward messages in qq to mc automatically (so you don't need to add "!!mc" prefix).
    "forward_join_message": true,  // should join messages be forwarded (only works if mc_to_qq_auto == true) 
    "admin": [],  // qq id of server admins, who can execute commands through the bridge
    "qq_list": [],  // blacklist/whitelist of qq group members
    "mc_list": [],  // blacklist/whitelist of minecraft players
    "qq_whitelist": false,  // Whether the bridge should work in whitelist mode. If true, members not in the qq_list will not be able to use message forwarding.
    "mc_whitelist": false  // same as above, but for minecraft
```

## Kaiheila bot client

`python ChatBridge.pyz kaiheila_bot`

Extra requirements (also listed in `/chatbridge/impl/kaiheila/requirements.txt`):

```
khl.py==0.0.10
```

Extra configure fields (compared to [CLI client](#cli-client))

```json5
    "client_id": "",  // kaiheila client id
    "client_secret": "",  // kaiheila client secret
    "token": "",  // kaiheila token
    "channels_for_command": [  // a list of channels, public commands can be used here. use string
        "123400000000000000",
        "123450000000000000"
    ],
    "channel_for_chat": "123400000000000000",  // the channel for chatting and private commands. use string
    "command_prefix": "!!",
    "client_to_query_stats": "MyClient1",  // it should be a client as an MCDR plugin, with stats_helper plugin installed in the MCDR
    "client_to_query_online": "MyClient2",  // a client described in the following section "Client to respond online command"
    "server_display_name": "TIS"  // The name of the server, used for display in some places
```

## Client to respond online command

```
python ChatBridge.pyz online_command
```

Extra requirements (also listed in `/chatbridge/impl/online/requirements.txt`):

```
parse
```

Extra configure fields (compared to [CLI client](#cli-client))

```json5
    "minecraft_list": [
        {
            "name": "survival",  // the name of the minecraft server (recommend value: the same as its name in bungeecord)
            "address": "127.0.0.1",  // the address of the server rcon
            "port": "25575",  // the port of the server rcon
            "password": "Server Rcon Password"  // the password of the server rcon
        }
    ],
    "bungeecord_list": [
        {
            "name": "BungeecordA",  // the name of the bungeecord server (unused value)
            "address": "127.0.0.1",  // the address of the bungeecord rcon
            "port": "39999",  // the port of the bungeecord rcon
            "password": "Bungee Rcon Password"  // the password of the bungeecord rcon
        }
    ],
    // The display order of the servers, optional
    // Servers not in the list will be thrown to the tail of the result and sorted in alphabetical order
    "display_order": [  
        "survival",  // Values are server names
        "creative"
    ]
```

CLI commands

- `online`, `!!online`: Display the current online players, mostly for testing
- `stop`: Stop the client
