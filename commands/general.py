import discord
from discord.ext import commands
from datetime import datetime


EMOJI_STATUS = {
    "online": "🟢",
    "idle": "🌙",
    "dnd": "🚫",
    "offline": "⚫"
}


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    #     self._cd = commands.CooldownMapping.from_cooldown(rate=1.0, per=3.0, type=commands.BucketType.user)
    #
    # async def cog_check(self, ctx):
    #     bucket = self._cd.get_bucket(ctx.message)
    #     retry_after = bucket.update_rate_limit()
    #     if retry_after:
    #         raise commands.CommandOnCooldown(bucket, retry_after, commands.BucketType.user)
    #     return True

    @commands.command()
    async def ping(self, ctx):
        time0 = discord.utils.snowflake_time(ctx.message.id).replace(tzinfo=None)
        ping = round(self.bot.latency * 1000)
        time1 = datetime.utcnow().replace(tzinfo=None)
        message = await ctx.reply(f":ping_pong: Pong! in: {ping} ms", mention_author=False)
        message_id = message.id
        time_diff1 = round((time1 - time0).microseconds / 1000)
        time_diff2 = round((discord.utils.snowflake_time(message_id).replace(tzinfo=None) - time1).microseconds / 1000)
        await message.edit(
            content=f":ping_pong: Pong! in: {ping} ms\nMessage received in: {time_diff1} ms\n"
                    f"Message sent in: {time_diff2} ms", allowed_mentions=discord.AllowedMentions.none())

    @commands.command()
    async def whois(self, ctx, user: discord.User = None):
        if not user:
            user = ctx.author
        yellow = 0xfff00
        await ctx.trigger_typing()
        flags = map(dirty_filter, user.public_flags.all()) if user.public_flags.value != 0 else ["None"]
        custom_embed = discord.Embed(title="User Data", description=f"Created at: "
                                                                    f"<t:{int(user.created_at.timestamp())}:D>\n"
                                                                    f"Bot: {user.bot} **|** System: {user.system}\n"
                                                                    f"Public Flags: "
                                                                    f"{', '.join(flags)}",
                                     color=yellow)
        custom_embed.set_author(name=f"{user.name}#{user.discriminator}", icon_url=user.avatar)
        member = ctx.guild.get_member(user.id)
        if member:
            boost = member.premium_since
            if not boost:
                boost = -1e+13
            else:
                print(boost)
                boost = boost.timestamp()
            custom_embed.add_field(name="Member info",
                                   value=f"Mobile:\u2800\u2800 {EMOJI_STATUS[member.mobile_status.value]}\n"
                                         f"Desktop:\u2800 {EMOJI_STATUS[member.desktop_status.value]}\n"
                                         f"Web:\u2800\u2800\u2800 {EMOJI_STATUS[member.web_status.value]}\n"
                                         f"Joined since: <t:{int(member.joined_at.timestamp())}:R>\n"
                                         f"Boosting since: <t:{int(boost)}:R>\n"
                                         f"Nick: {member.nick}",
                                   inline=False)   # no spaces? fine I'll do it myself
        await ctx.send(embed=custom_embed)

    @commands.command(aliases=["av"])
    async def avatar(self, ctx, user: discord.User = None):
        """
        Shows global user avatar
        """
        if not user:
            user = ctx.author
        embed = discord.Embed(title='Avatar')
        embed.set_author(name=user.name, icon_url=user.avatar)
        embed.set_image(url=user.avatar)
        await ctx.send(embed=embed)

    @commands.command(aliases=["av2"])
    async def avatar2(self, ctx, user: discord.Member = None):
        """
        Avatar V2!! with ~~useless~~ updated feature
        """
        if not user:
            user = ctx.author
        embed = discord.Embed(title='Avatar')
        embed.set_author(name=user.display_name, icon_url=user.display_icon)
        embed.set_image(url=user.guild_avatar)
        await ctx.send(embed=embed)

    @commands.command()
    async def banner(self, ctx, user: discord.User = None):
        """
        Returns a user's Discord banner
        """
        # PENDING: below code only execute in 2.0 which waiting to be released
        if not user:
            user = ctx.author
        member = await self.bot.fetch_user(user.id)
        banner_url = member.banner
        if not banner_url:
            banner_url = "https://c4.wallpaperflare.com/wallpaper/" \
                         "357/645/211/easter-island-chile-starry-night-statue-wallpaper-preview.jpg"

        custom_embed = discord.Embed(description=f"{member.name}'s banner")
        custom_embed.set_image(url=banner_url)
        await ctx.send(embed=custom_embed)


def dirty_filter(text):
    """
    Function to filter dot underscore in PublicFlag and title them
    Args:
        text (Any): text to filter
    Returns:
        str: Filtered text
    """
    return text.name.split('.')[-1].replace('_', ' ').title()


async def setup(bot):
    await bot.add_cog(General(bot))
