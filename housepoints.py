#harrypotter points
#p!{house_initial(g/r/h/s} {remove/add} {points}
#!housepoints/hp shows scoreboard

from discord.ext import commands
from cogs.util import pyson
import discord


def is_owner():
    def predictate(ctx):
        if ctx.author is ctx.guild.owner:
            return True
        return False
    return commands.check(predictate)

class housepoints:
    def __init__(self, bot):
        self.bot = bot
        self.bot.hp = pyson.Pyson('data/harrypotter/data.json')
        self.houses = {
            "g": 'Gryffindor',
            "r": 'Ravenclaw',
            "h": 'Hufflepuff',
            "s": 'Slytherin'
        }

    @is_owner()
    async def on_message(self, message):
        if message.content.startswith('p!'):
            if message.content[2] in self.houses:
                split_message = message.content.split()
                if split_message[0] == f'p!{message.content[2]}':
                    if split_message[1] == 'add' or split_message[1] == 'remove':
                        if split_message[2].isdigit():
                            if split_message[1] == 'add':
                                old_points = self.bot.hp.data.get('housepoints').get(self.houses.get(message.content[2])).get('points')
                                self.bot.hp.data['housepoints'][self.houses.get(message.content[2])]['points'] = old_points + int(split_message[2])
                                self.bot.hp.save()
                                await message.channel.send('added')
                            if split_message[1] == 'remove':
                                old_points = self.bot.hp.data.get('housepoints').get(self.houses.get(message.content[2])).get('points')
                                self.bot.hp.data['housepoints'][self.houses.get(message.content[2])]['points'] = old_points - int(split_message[2])
                                self.bot.hp.save()
                                await message.channel.send('removed')

    @commands.command(aliases=['hp'])
    async def housepoints(self, ctx):
        embed = discord.Embed(colour=discord.Colour(0x278d89))
        house_list = ''
        for item in self.bot.hp.data.get('housepoints'):
            points = self.bot.hp.data.get('housepoints').get(item).get('points')
            house_list += f'**{item}**: {points}\n'

        embed.add_field(name='House', value=house_list)
        await ctx.send(embed=embed)




def setup(bot):
    bot.add_cog(housepoints(bot))
