import aiohttp
import re
import json
from discord.ext import commands

with open('./data/node.json', mode='r') as data_file:
    Nodes = json.loads(data_file.read())

class Warframe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.url = 'http://content.warframe.com/dynamic/worldState.php'
    
    @commands.command(pass_context=True)
    async def alerts(self, ctx):
        ''' Get alerts from the Warframe world state. '''
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as res:
                if res.status == 200:
                    data = await res.json(content_type='text/html')
                    await ctx.message.channel.send('**Alerts:**')
                    for alert in data['Alerts']:
                        if alert['MissionInfo']['location'] in Nodes:
                            mission_node = Nodes[alert['MissionInfo']['location']]
                            planet = re.findall(r'([A-Z]\w+)', mission_node)[0]
                            city = re.findall(r'([A-Z]\w+)', mission_node)[1]
                            node = '{} ({})'.format(city, planet)
                        mission_type = alert['MissionInfo']['missionType'].replace('MT_', '').replace('_', ' ').title()
                        faction = alert['MissionInfo']['faction'].replace('FC_', '').title()
                        min_enemy_level = alert['MissionInfo']['minEnemyLevel']
                        max_enemy_level = alert['MissionInfo']['maxEnemyLevel']
                        reward_credits = alert['MissionInfo']['missionReward']['credits']
                        reward_items = []
                        if 'items' in alert['MissionInfo']['missionReward']:
                            for item in alert['MissionInfo']['missionReward']['items']:
                                if 'AlertFusionBundleMedium' in item:
                                    reward_items.append('100 Endo')
                                else:
                                    index = item.rfind('/') + 1
                                    name = re.sub(r'(?<=[.,])(?=[^\s])', r' ', item[index:])
                                    reward_items.append(re.sub(r'(\w)([A-Z])', r'\1 \2', name))
                        if 'countedItems' in alert['MissionInfo']['missionReward']:
                            for item in alert['MissionInfo']['missionReward']['countedItems']:
                                if 'Alertium' in item['ItemType']:
                                    reward_items.append('Nitan Extract')
                                elif 'Oxium' in item['ItemType']:
                                    reward_items.append('Oxium ({})'.format(item['ItemCount']))
                                else:
                                    index = item['ItemType'].rfind('/') + 1
                                    name = re.sub(r'(?<=[.,])(?=[^\s])', r' ', item['ItemType'][index:])
                                    reward_items.append('{} ({})'.format(re.sub(r'(\w)([A-Z])', r'\1 \2', name), item['ItemCount']))
                            
                        response = '{} | {} - {} | ({}-{}) | Rewards: {} Credits'.format(node, faction, mission_type, min_enemy_level, max_enemy_level, reward_credits)
                        for item in reward_items:
                            response += ', {}'.format(item)
                        await ctx.message.channel.send(response)
            await session.close()

    @commands.command(pass_context=True)       
    async def events(self, ctx):
        ''' Get events from the Warframe world state. '''
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as res:
                if res.status == 200:
                    data = await res.json(content_type='text/html')
                    await ctx.message.channel.send('**Events:**')
                    for event_item in data['Events']:
                        if event_item['Messages'][0]['LanguageCode'] == "en":
                            await ctx.message.channel.send('[{}]({})'.format(event_item['Messages'][0]['Message'], event_item['Prop']))
            await session.close()
    
    @commands.command(pass_context=True)
    async def sortie(self, ctx):
        ''' Get sortie mission info from the Warframe world state. '''
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as res:
                if res.status == 200:
                    data = await res.json(content_type='text/html')
                    await ctx.message.channel.send('**Sortie Missions:**')
                    for mission in data['Sorties'][0]['Variants']:
                        mission_type = mission['missionType'].replace('MT_','').replace('_', ' ').title()
                        modifier = mission['modifierType'].replace('SORTIE_MODIFIER_', '').replace('_', ' ').title()
                        if mission['node'] in Nodes:
                            mission_node = Nodes[mission['node']]
                            planet = re.findall(r'([A-Z]\w+)', mission_node)[0]
                            city = re.findall(r'([A-Z]\w+)', mission_node)[1]
                            node = '{} ({})'.format(city, planet)
                        else:
                            node = 'Unknown Node'
                        if 'Grineer' in mission['tileset']:
                            faction = 'Grineer'
                        elif 'Corpus' in mission['tileset']:
                            faction = 'Corpus'
                        elif 'Infested' in mission['tileset']:
                            faction = 'Infested'
                        else:
                            faction = 'Unknown'
                        await ctx.message.channel.send('{} | {} ({}) | {}'.format(node, mission_type, modifier, faction))
            await session.close()