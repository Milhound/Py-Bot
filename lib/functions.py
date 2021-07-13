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
        if number == 1:
            result = 'Heads'
        elif number == 2:
            result = 'Tails'
        await ctx.message.channel.send(result)

    @commands.command(pass_context=True)
    async def dice(self, ctx):
        """ Rolls a dice. """
        try:
            dice_size = int(ctx.message.content.split(' ')[1])
            result = random.randint(1, dice_size)
            await ctx.message.channel.send(result)
        except ValueError:
            print('[!] Dice Command Error: Not a number. ({})'.format(ctx.message.content.split(' ')[1]))
            result = 'Error not a number.'
            await ctx.message.channel.send(result)
        except IndexError:
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
            try:
                url ='https://www.googleapis.com/youtube/v3/search?type=video&part=snippet&q=' + query + '&key=' + str(os.environ.get('Google_API'))
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as res:
                        if res.status == 200:
                            data = await res.json()
                            await ctx.message.channel.send('https://www.youtube.com/watch?v=' + data['items'][0]['id']['videoId'])
                        elif res.status == 403:
                            await ctx.message.channel.send("Something is wrong with the API Token. Error code: 403 - Forbidden")
                        else:
                            await ctx.message.channel.send('HTTP Error code: ' + str(res.status))
                    await session.close()
            except Exception as err:
                await ctx.message.channel.send(err)
        else:
            await ctx.message.channel.send('Please add a query to your request.')

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