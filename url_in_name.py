#just a simple thrown together check for url's in names n kick em.
from urlextract import URLExtract


class urlcheck:
    def __init__(self, bot):
        self.bot = bot

    async def on_member_join(self, member):
        extractor = URLExtract()
        urls = extractor.find_urls(f'{member.name}')
        if not urls:
            print('no urls found good to go')
        else:
            print(urls)
            await member.guild.kick(member)


def setup(bot):
    bot.add_cog(urlcheck(bot))
