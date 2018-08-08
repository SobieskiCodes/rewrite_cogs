#set up a channel for text to be moved to on a command
#eg: !t2c <some text you want to move> | the bot will remove the message and post it in the channel you provide.

from discord.ext import commands


def is_owner():
    def predictate(ctx):
        if ctx.author is ctx.guild.owner:
            return True
        return False
    return commands.check(predictate)


class textmovechannels:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def t2c(self, ctx):
        ''': t2c <text>'''
        if str(ctx.guild.id) not in self.bot.promo.data.get('servers'):
            await ctx.send('No t2c channel set yet, try setting it first with "smc".')
            return

        channel_name = self.bot.promo.data.get('servers').get(str(ctx.guild.id)).get('channel_to_send_to')
        if any(channel.name == channel_name for channel in ctx.guild.text_channels):
            for channel in ctx.guild.text_channels:
                if channel.name == channel_name:
                    prefix = self.bot.config.data.get('servers').get(str(ctx.guild.id)).get('prefix')
                    new_content = str(ctx.message.content).replace('{0}{1.command.qualified_name}'.format(prefix, ctx), '')
                    await channel.send(f'{ctx.message.author.name}: {new_content}')
                    await ctx.message.delete()

    @is_owner()
    @commands.command(aliases=['smc'])
    async def setmovechannel(self, ctx, channel_name: str=None):
        ''': setmovechannel <channel name>'''
        if not channel_name:
            await ctx.send('No channel specified')
            return

        if any(channel.name == channel_name for channel in ctx.guild.text_channels):
            for channel in ctx.guild.text_channels:
                if channel.name == channel_name:
                    new_channel = {'channel_to_send_to': channel.name}
                    self.bot.promo.data['servers'][f'{str(ctx.guild.id)}'] = new_channel
                    self.bot.promo.save()
                    await ctx.send(f'Channel to move to set to "{channel_name}".')
                    return

        else:
            await ctx.send(f'couldnt find a channel named {channel_name}')


def setup(bot):
    bot.add_cog(textmovechannels(bot))
