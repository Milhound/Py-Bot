import logging
import os

import discord

from discord.ext import commands
from lib.voice import Voice
from lib.functions import Text
from lib.wow import Guild
from lib.warframe import Warframe

bot = commands.Bot(command_prefix=commands.when_mentioned_or('$'))
bot.add_cog(Text(bot))
bot.add_cog(Voice(bot))

@bot.event
async def on_ready():
    print('[*] Logged in as:')
    print('[*] {} - {}'.format(bot.user.name, bot.user.id))
    print('----------')
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='./data/discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

@bot.event
async def on_resumed():
    print('reconnected')

if os.environ.get("PY_BOT_TOKEN") is None:
    print('[!] Failed to load Py Bot\'s token from System Environment Variables.')
    exit()
else:
    bot.run(os.environ.get("PY_BOT_TOKEN"), reconnect=True)