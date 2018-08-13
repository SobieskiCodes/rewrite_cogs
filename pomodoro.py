from cogs.util import pyson
from discord.ext import commands
import asyncio
import discord


def pomo_channel():
    def does_it_exist(ctx):
        if ctx.channel.name == 'task-trade':
            return True
        return False
    return commands.check(does_it_exist)


class pomodoro:
    def __init__(self, bot):
        self.bot = bot
        self.bot.pomo = pyson.Pyson('data/pomodoro/data.json')

    async def pomodoro_timer(self, ctx, author):
        while author in self.bot.pomo.data.get('timers'):
            counter = self.bot.pomo.data.get('timers').get(author).get('counter')
            repeat = self.bot.pomo.data.get('timers').get(author).get('repeat')
            if counter < repeat:
                first_sleep = self.bot.pomo.data.get('timers').get(author).get('length')
                await asyncio.sleep(first_sleep)
                if author in self.bot.pomo.data.get('timers'):
                    if counter >= repeat:
                        break
                    mention_list = []
                    for x in self.bot.pomo.data.get('timers').get(author):
                        contains = ['length', 'break', 'repeat', 'counter']
                        if x not in contains:
                            mention_list.append(x)

                    mention_list.append(author)
                    msg = ', '.join(ctx.channel.guild.get_member(int(y)).mention for y in mention_list)
                    await ctx.send(f'Time to take a break {msg}')
                    break_time = self.bot.pomo.data.get('timers').get(author).get('break')
                    await asyncio.sleep(break_time)
                    if author in self.bot.pomo.data.get('timers'):
                        if counter >= repeat:
                            break
                        self.bot.pomo.data['timers'][author]['counter'] += 1
                        self.bot.pomo.save()
                        await ctx.send(f'Back to work {msg}')

            if counter >= repeat:
                break

            else:
                break

        self.bot.pomo.data['timers'].pop(author, None)
        self.bot.pomo.save()

    @pomo_channel()
    @commands.command()
    async def startwork(self, ctx, person: str = None, number_of_pomo: int = 1, length: int = 25,
                        time_break: int = 5):
        ''': startwork [mention] [number_of_pomos] [session length] [break length]
        all params are optional, defaults are no partner, one time, 25m, 5m.
        if you want to adjust one param you need to add them all in the order provided.
        Examples:
        !startwork [@mention] [number of repeats] [work time] [break time]
        !startwork [@mention]
        !startwork [number of repeats] [work time] [break time]
        !startwork <all defaults>
        '''
        if str(ctx.author.id) in self.bot.pomo.data.get('timers'):
            await ctx.send("You already have an active timer going!")
            return

        if not person:
            number_of_pomo = 1
            length = 25
            time_break = 5
            new_timer = {'length': length * 60, 'break': time_break * 60, 'repeat': number_of_pomo, 'counter': 0}
            self.bot.pomo.data['timers'][str(ctx.message.author.id)] = new_timer
            self.bot.pomo.save()

            await ctx.send(f'Pomodoro started for {ctx.message.author.mention} '
                           f'with {number_of_pomo} sessions, {length} minute sessions, and {time_break} minute breaks.')
            await self.pomodoro_timer(ctx, str(ctx.author.id))

        elif person.isdigit():
            time_break = int(length)
            length = int(number_of_pomo)
            number_of_pomo = int(person)
            person = None

            if not int(length) or not int(time_break) or not int(number_of_pomo):
                await ctx.send('the times you provided are not valid numbers.')
                return

            new_timer = {'length': length * 60, 'break': time_break * 60, 'repeat': number_of_pomo, 'counter': 0}
            self.bot.pomo.data['timers'][str(ctx.message.author.id)] = new_timer
            self.bot.pomo.save()

            await ctx.send(f'Pomodoro started for {ctx.message.author.mention} '
                           f'with {number_of_pomo} sessions, {length} minute sessions, and {time_break} minute breaks.')
            await self.pomodoro_timer(ctx, str(ctx.author.id))

        elif person and not person.isdigit():
            if not ctx.message.raw_mentions:
                await ctx.send('no mentions')
                return

            if ctx.message.raw_mentions[0] == ctx.author.id:
                await ctx.send('you cant join your own session goober')
                return

            if not int(length) or not int(time_break) or not int(number_of_pomo):
                await ctx.send('the times you provided are not valid numbers.')
                return

            mention_person = ctx.message.guild.get_member(ctx.message.raw_mentions[0])
            new_timer = {str(mention_person.id): True, 'length': length * 60, 'break': time_break * 60, 'repeat':
                number_of_pomo, 'counter': 0}

            self.bot.pomo.data['timers'][str(ctx.message.author.id)] = new_timer
            self.bot.pomo.save()

            await ctx.send(f'Pomodoro started for {ctx.message.author.mention} and {mention_person.mention} '
                           f'with {number_of_pomo} sessions, {length} minute sessions, and {time_break} minute breaks.')
            await self.pomodoro_timer(ctx, str(ctx.author.id))

    @pomo_channel()
    @commands.command()
    async def adjustwork(self, ctx, adjust: str = None, time: str = None):
        ''': adjustwork <length/break> <time in minutes>'''
        if not adjust or not time:
            await ctx.send('it seems you didnt specify what to adjust! or time is invalid')
            return

        if not time.isdigit():
            await ctx.send('time isnt a valid digit!')
            return

        contains = ['break', 'length']
        if adjust.lower() not in contains:
            await ctx.send('it seems you didnt specify what to adjust! valid format is length/break')
            return

        if str(ctx.author.id) not in self.bot.pomo.data.get('timers'):
            await ctx.send('it seems you dont have any active timers!')
            return

        else:
            set_time = int(time) * 60
            self.bot.pomo.data['timers'][str(ctx.message.author.id)][adjust] = set_time
            self.bot.pomo.save()
            await ctx.send(f'{adjust} has been updated to {time}.')

    @pomo_channel()
    @commands.command()
    async def endwork(self, ctx):
        ''': endwork ends a pomodoro if you have one running'''
        if str(ctx.author.id) in self.bot.pomo.data.get('timers'):
            self.bot.pomo.data['timers'].pop(str(ctx.author.id), None)
            self.bot.pomo.save()
            await ctx.send('your pomodoro has been canceled')

        else:
            await ctx.send('you dont have an active timer.')

    @pomo_channel()
    @commands.command()
    async def joinwork(self, ctx, person: str=None):
        ''': joinwork <mention> allows you to join an ongoing pomodoro'''
        if not person:
            await ctx.send('please tell me whos pomodoro you want to join')
            return

        if not ctx.message.raw_mentions[0]:
            await ctx.send('please only mention one person')
            return

        if ctx.message.raw_mentions[0] == ctx.author.id:
            await ctx.send('you cant join your own session goober')
            return
        if str(ctx.author.id) in self.bot.pomo.data.get('timers'):
            await ctx.send('you have an active timer going, i dont think you should be joining sessions')
            return

        if str(ctx.message.raw_mentions[0]) in self.bot.pomo.data.get('timers'):
            if str(ctx.message.author.id) not in self.bot.pomo.data.get('timers').get(str(ctx.message.raw_mentions[0])):
                self.bot.pomo.data['timers'][str(ctx.message.raw_mentions[0])][str(ctx.author.id)] = True
                self.bot.pomo.save()
                await ctx.send('pomodoro joined!')
                return

            else:
                await ctx.send('it seems you are already in that pomodoro')
                return

        else:
            await ctx.send(f'i couldnt find a pomodoro going for {person}')

    @pomo_channel()
    @commands.command()
    async def leavework(self, ctx, person: str = None):
        ''': leavework <mention> allows you to leave an ongoing pomodoro'''
        if not person:
            await ctx.send('please tell me whos pomodoro you want to leave')
            return

        if not ctx.message.raw_mentions[0]:
            await ctx.send('please only mention one person')
            return

        if ctx.message.raw_mentions[0] == ctx.author.id:
            await ctx.send('you can just use !endwork')
            return

        if str(ctx.message.raw_mentions[0]) in self.bot.pomo.data.get('timers'):
            if str(ctx.message.author.id) in self.bot.pomo.data.get('timers').get(str(ctx.message.raw_mentions[0])):
                self.bot.pomo.data['timers'][str(ctx.message.raw_mentions[0])].pop(str(ctx.author.id), None)
                self.bot.pomo.save()
                await ctx.send('pomodoro left!')
                return

            else:
                await ctx.send('it seems you arent in that work group.')
                return

        else:
            await ctx.send(f'i couldnt find a pomodoro going for {person}')

    @pomo_channel()
    @commands.command()
    async def worksessions(self, ctx):
        ''': worksessions lists all ongoing work sessions'''
        embed = discord.Embed()
        session_list = ''
        for timer in self.bot.pomo.data.get('timers'):
            if not timer:
                pass
            length = self.bot.pomo.data.get('timers').get(timer).get('length')
            break_time = self.bot.pomo.data.get('timers').get(timer).get('break')
            starter_member = ctx.message.guild.get_member(int(timer))
            member_list = ''
            for item in self.bot.pomo.data.get('timers').get(timer):
                contains = ['break', 'repeat', 'counter', 'length']
                if item not in contains:
                    member = ctx.message.guild.get_member(int(item))
                    member_list += f'{member.name} '
            if not member_list:
                member_list = 'None'

            session_list += f'**Session Starter**: {starter_member.name} \n**Session Length**:{length // 60}m ' \
                            f'\n**Break Time**:{break_time // 60}m \n**Members**:{member_list} \n \n'

        if session_list:
            embed.add_field(name='Sessions', value=f'{session_list}', inline=True)

        else:
            embed.add_field(name='Nothing to show', value='Seems there are no timers going.')

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(pomodoro(bot))
