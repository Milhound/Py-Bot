import json
import aiohttp
import asyncio
from discord.ext import commands

with open('./data/spec_info.json') as data_file:
        Config = json.loads(data_file.read())

class Guild:
    """ Comprehensive function list for the blizzard wow api. """
    def __init__(self, bot):
        self.bot = bot
        self.classes = Config['classList']

    async def get_members(self):
        if os.environ.get("WoW_Token") is None:
            return
        else:
            url = 'https://us.api.battle.net/wow/guild/Zul\'jin/Legion%20Invasion?fields=members&locale=en_US&apikey=' + os.environ.get("WoW_Token")
            async with aiohttp.ClientSession().get(url) as res:
                if res.status == 200:
                    data = await res.json()
                    with open('guild.json', 'w') as f:
                        json.dump(data, f)
                    return data

    @commands.command(pass_context=True)
    async def class_count(self, ctx):
        data = await self.get_members()
        result = []
        counter = []
        for item in data['members']:
            counter.append(int(item['character']['class']))
        for x in range(0, 12):
            result.append('{}: {}'.format(self.classes[x], counter.count(x)))
        await ctx.message.channel.send('Class count for Legion Invasion - Zul\'jin:')
        for value in result:
            await ctx.message.channel.send(value)

    @commands.command(pass_context=True)
    async def class_count_110(self):
        data = await self.get_members()
        result = []
        counter = []
        for item in data['members']:
            if int(item['character']['level']) == 110:
                counter.append(int(item['character']['class']))
        for x in range(0, 12):
            result.append('{}: {}'.format(self.classes[x], counter.count(x)))
        await ctx.message.channel.send('Class count for Legion Invasion - Zul\'jin @ 110:')
        for value in result:
            await ctx.message.channel.send(value)

    # TODO
    async def get_titles(self, player, target):
        player_titles = []
        target_titles = []
        if os.environ.get("WoW_Token") is None:
            return
        else:
            player_url = 'https://us.api.battle.net/wow/character/Zuljin/' + player + '?fields=titles&locale=en_US&apikey=' + os.environ.get("WoW_Token")
            async with aiohttp.ClientSession().get(player_url) as res:
                if res.status == 200:
                    player = res.json()
            target_url = 'https://us.api.battle.net/wow/character/Zuljin/' + target + '?fields=titles&locale=en_US&apikey=' + os.environ.get("WoW_Token")
            async with aiohttp.ClientSession().get(target_url) as res:
                if res.status == 200:
                    target = res.json()
           
            for title in player['titles']:
                player_titles.append(title['name'])
            for title in target['titles']:
                target_titles.append(title['name'])
            
            titles_target_unobtained = set(player_titles).difference(set(target_titles))
            diffrent_titles = set(target_titles).difference(set(player_titles))
            return titles_target_unobtained, diffrent_titles

class Pvp:
    """A series of methods for wow's pvp system"""

    def __init__(self, bot):
        self.bot = bot
        self.classes = Config['classList']
        self.specs = Config['specList']

    async def get_players(self):
        """Grab the current top 3v3 arena players"""
        if os.environ.get("WoW_Token") is None:
            return
        else:
            async with aiohttp.ClientSession().get('https://us.api.battle.net/wow/leaderboard/3v3?locale=en_US&apikey=' + os.environ.get("WoW_Token")) as res:
                if res.status == 200:
                    data = await res.json()
                    output = {}
                    for player in range(0, 965):
                        output[int(player)] = data['rows'][player]
                    with open('Pvp_Players.json', 'w') as pvp_players:
                        json.dump(output, pvp_players)
                    return output

    @commands.command(pass_context=True)
    async def top_10_class(self):
        """List the top 10 player's class and their counts"""
        players = await self.get_players()
        classes = []
        # Add all players
        for player in players:
            classes.append(int(player['classId']))
        del classes[10:]
        await self.bot.send_message('Top 10 3v3 Composition:')
        for xvar in range(1, 13):
            if players.count(xvar) > 0:
                await self.bot.send_message('{:s}: {:d}'.format(self.classes[xvar - 1], classes.count(xvar)))

    @commands.command(pass_context=True)
    async def top_100_class(self):
        """List the top 100 player's class and their counts"""
        players = self.get_players()
        classes = []
        for player in players:
            classes.append(player['classId'])
        del classes[100:]
        await self.bot.send_message('Top 100 3v3 Composition:')
        for xvar in range(1, 13):
            if classes.count(xvar) > 0:
                await self.bot.send_message('{:s}: {:d}'.format(self.classes[xvar - 1], classes.count(xvar)))

    @commands.command(pass_context=True)
    async def top_specs(self):
        """List all of the top player's specs and their count"""
        players = await self.get_players()
        specs = []
        for player in players:
            specs.append(player['specId'])
        await self.bot.send_message('Top 3v3 Composition:')
        for key in self.specs:
            if specs.count(int(key)) > 0:
                await self.bot.send_message('{:s}: {:d} ({:.2f}%)'.format(
                    self.specs[key],
                    specs.count(int(key)),
                    float(specs.count(int(key))/965.0)*100)
                     )

    @commands.command(pass_context=True)
    async def top_10_specs(self):
        """List the top 10 player's specs and their counts"""
        players = await self.get_players()
        specs = []
        for player in players:
            specs.append(player['specId'])
        del specs[10:]
        await ctx.message.channel.send('Top 10 3v3 Composition:')
        for key in self.specs:
            if specs.count(int(key)) > 0:
                await ctx.message.channel.send('{:s}: {:d}'.format(self.specs[key], specs.count(int(key))))

    @commands.command(pass_context=True)
    async def top_100_specs(self):
        """List the top 100 player's specs and their counts"""
        players = await self.get_players()
        specs = []
        for player in players:
            specs.append(player['specId'])
        del specs[100:]
        print('Top 100 3v3 Composition:')
        for key in self.specs:
            if specs.count(int(key)) > 0:
                await ctx.message.channel.send('{:s}: {:d}'.format(self.specs[key], specs.count(int(key))))
    
    @commands.command(pass_context=True)
    async def rating_req(self, ctx):
        """Give the rating and stats of the lowest ranked player '965'"""
        data = await self.get_players()
        await self.bot.send_message(ctx.message.channel, "Rating: {:d}".format(data['964']['rating']))
        await self.bot.send_message(ctx.message.channel, "Season Wins: {:d}".format(data['964']['seasonWins']))
        await self.bot.send_message(ctx.message.channel, "Season Losses: {:d}".format(data['964']['seasonLosses']))
        await self.bot.send_message(ctx.message.channel, "Ratio: {:.4f}".format(float(data['964']['seasonWins']) / float(data['964']['seasonLosses'])))

    @commands.command(pass_context=True)
    async def player_ratio(self, ctx):
        """Get player statistics for current season"""
        player = ctx.message.content.split(' ')[1]
        if os.environ.get("WoW_Token") is None:
            return
        else:
            async with aiohttp.ClientSession().get('https://us.api.battle.net/wow/character/zul\'jin/' + player + '?fields=pvp&locale=en_US&apikey=' + os.environ.get("WoW_Token")) as res:
                if res.status == 200:
                    data = await res.json()
                    player_pvp_stats = data['pvp']['brackets']['ARENA_BRACKET_3v3']
                    await ctx.message.channel.send(u"Player: {:s}").format(player)
                    await ctx.message.channel.send("Rating: {:d}".format(player_pvp_stats['rating']))
                    await ctx.message.channel.send("Season Wins: {:d}".format(player_pvp_stats['seasonWon']))
                    await ctx.message.channel.send("Season Losses: {:d}".format(player_pvp_stats['seasonLost']))

                    if player_pvp_stats['seasonWon'] == 0 or player_pvp_stats['seasonLost'] == 0:
                        await ctx.message.channel.send("Ratio: 0")
                    else:
                        await ctx.message.channel.send("Ratio: {:.4f}".format(
                            float(player_pvp_stats['seasonWon'])/
                            float(player_pvp_stats['seasonLost']))
                            )
            
