#checks for discord.py updates every hour and posts them to a channel.
#replies with no changes if none (can remove obviously)
#if too large for embed sends to hastebin


from discord.ext import commands
import discord
import difflib
import os
import asyncio
channel_id = 466672582222151680
whats_new_url = 'https://raw.githubusercontent.com/Rapptz/discord.py/master/docs/whats_new.rst'


class DpyUpdates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_url(self, content):
        async with self.bot.aiohttp.post('https://haste.discordbots.mundane.tk/documents',
                                        data=content.encode('utf-8')) as resp:
            if resp.status == 200:
                key = await resp.json()
                url = f'https://haste.discordbots.mundane.tk/{key["key"]}.txt'
                return url
            else:
                return 'invalid'

    async def download(self, filename):
        if not os.path.exists(f"./{filename}"):
            async with self.bot.aiohttp.get(url=whats_new_url) as resp:
                with open(filename, 'wb') as f_handle:
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        f_handle.write(chunk)
                return await resp.release()

    async def main(self, time: int = 3600):
        print('here')
        while True:
            if not os.path.exists(f"./current_whats_new.txt"):
                await DpyUpdates.download(self, "current_whats_new.txt")
            else:
                await DpyUpdates.download(self, "downloaded_whats_new.txt")
                with open("current_whats_new.txt") as f, open('downloaded_whats_new.txt') as g:
                    flines = f.readlines()
                    glines = g.readlines()
                    d = difflib.Differ()
                    diff = d.compare(flines, glines)

                only_additions = []
                for line in diff:
                    if line.startswith('+ ') and not line[2:].isspace():
                        only_additions.append(line[2:])
                channel = await self.bot.fetch_channel(channel_id)
                if only_additions:
                    test = '\n'.join(only_additions)
                    if len(test) <= 2000:
                        e = discord.Embed(title='New Version of Discord.py out.', colour=discord.Colour(0x278d89),
                                          description=f"```{test}```")
                    elif len(test) >= 2001:
                        message = 'The changes would exceed discord message length limit, here is the '
                        content = await DpyUpdates.get_url(self, test)
                        if content != 'invalid':
                            description = f'{message} [hastebin]({content}).'
                            e = discord.Embed(colour=discord.Colour(0x278d89), description=description)
                        else:
                            message = 'The reply would exceed discord message length limit, and hastebins.'
                            e = discord.Embed(colour=discord.Colour(0x278d89), description=f'{message}')
                    with open("current_whats_new.txt", 'w') as f, open('downloaded_whats_new.txt') as g:
                        for line in g.readlines():
                            f.write(line)

                    await channel.send(embed=e)

                else:
                    await channel.send('No changes')

                os.remove('downloaded_whats_new.txt')

            await asyncio.sleep(time)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(DpyUpdates.main(self))


def setup(bot):
    bot.add_cog(DpyUpdates(bot))
