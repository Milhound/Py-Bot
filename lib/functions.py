import random
import asyncio
import os
import aiohttp
from discord.ext import commands

class Text(commands.Cog):
    """Text related commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        await ctx.message.channel.send("Pong")

    @commands.command(pass_context=True)
    async def coin(self, ctx):
        """ Flips a coin. """
        number = random.randint(1,2)
        if number is 1:
            result = 'Heads'
        elif number is 2:
            result = 'Tails'
        await ctx.message.channel.send(result)
    @commands.command(pass_context=True)
    async def dice(self, ctx):
        """ Rolls a dice. """
        if ctx.message.content.split(' ')[1] is not None:
            try:
                dice_size = int(ctx.message.content.split(' ')[1])
                result = random.randint(1, dice_size)
            except ValueError:
                print('[!] Dice Command Error: Not a number. ({})'.format(ctx.message.content.split(' ')[1]))
                result = 'Error not a number.'
                await ctx.message.channel.send(result)
        else:
            result = random.randint(1, 6)
            await ctx.message.channel.send(result)
    @commands.command(pass_context=True)
    async def f(self, ctx):
        """ Convert a Celcius temperature to Fahrenheit... """
        try:
            value = int(ctx.message.content.split(' ')[1])
            result = int(value * 1.8 + 32)
        except ValueError:
            print('[!] Celcius Conversion Error: Not a number. ({})'.format(ctx.message.content.split(' ')[1]))
            result = 'Error not a number.'
        await ctx.message.channel.send(result)
    @commands.command(pass_context=True)
    async def c(self, ctx):
        """ Convert a Fahrenheit temperature to Celcius. """
        try:
            value = int(ctx.message.content.split(' ')[1])
            result = int((value - 32) * (5 / 9))
        except ValueError:
            print('[!] Fahrenheit Conversion Error: Not a number. ({})'.format(ctx.message.content.split(' ')[1]))
            result = 'Error not a number.'
        await ctx.message.channel.send(result)
    @commands.command(pass_context=True)
    async def yt(self, ctx):
        """ Search YouTube and return a video """
        if ctx.message.content.split(' ')[1]:
            query = ctx.message.content[3:].strip().replace(' ', '%20')
            url ='https://www.googleapis.com/youtube/v3/search?type=video&part=snippet&q=' + query + '&key=' + 'AIzaSyDRYzHDqlWJxwBOH8iU2U_g3lg5o6eKDaM'
            async with aiohttp.ClientSession().get(url) as res:
                if res.status == 200:
                    data = await res.json()
                    await ctx.message.channel.send('https://www.youtube.com/watch?v=' + data['items'][0]['id']['videoId'])
        else:
            self.bot.say('Please add a query to your request.')
    @commands.command(pass_context=True)
    async def ud(self, ctx):
        """ Look up Urban Dictionary definition of a word. """
        if ctx.message.content.split(' ')[1]:
            query = ctx.message.content[3:].strip().replace(' ', '%20')
            url = 'http://api.urbandictionary.com/v0/define?term=' + query
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as res:
                    if res.status == 200:
                        data = await res.json()
                        await ctx.message.channel.send('```Word: {}\nDefinition: {}```'.format(data['list'][0]['word'], data['list'][0]['definition']))
                await session.close()