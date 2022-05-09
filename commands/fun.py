from collections import defaultdict
from os import getenv
import random

import discord
from discord.ext import commands


TOKEN = getenv("ANIME_TOKEN")


class Action(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emoji_cache = defaultdict(lambda: [None])  # tricky way to pass list of None to random choice
    #     self._cd = commands.CooldownMapping.from_cooldown(rate=1.0, per=3.0, type=commands.BucketType.user)
    #
    # async def cog_check(self, ctx):
    #     bucket = self._cd.get_bucket(ctx.message)
    #     retry_after = bucket.update_rate_limit()
    #     if retry_after:
    #         raise commands.CommandOnCooldown(bucket, retry_after, commands.BucketType.user)
    #     return True

    async def get_gif(self, endpoint: str):
        if random.random() > 0.75 or endpoint not in self.emoji_cache:
            api = f"https://kawaii.red/api/gif/{endpoint}/token={TOKEN}"
            key = "response"
            if endpoint in {"pat", "hug"}:
                api = f"https://some-random-api.ml/animu/{endpoint}"
                key = "link"

            async with self.bot.session.get(api) as r:
                if r.status != 200:
                    return random.choice(self.emoji_cache[endpoint]) or None
                response = await r.json()
                link = response[key]
                if endpoint not in self.emoji_cache:
                    self.emoji_cache.update({endpoint: [link]})
                else:
                    self.emoji_cache[endpoint].append(link)
                    self.emoji_cache[endpoint] = list(set(self.emoji_cache[endpoint]))
                return link
        else:
            return random.choice(self.emoji_cache[endpoint])

    @commands.command()
    async def slap(self, ctx, user: discord.User):
        """Feels angy? slap them"""
        response = await self.get_gif("slap")
        if response is None:
            return await ctx.send("Something went wrong :c")
        custom_embed = discord.Embed(title="Slap",
                                     description=f"{ctx.author.name} slaps {user.name}",
                                     color=discord.Colour.random())
        custom_embed.set_image(url=response)
        await ctx.send(embed=custom_embed)

    @commands.command()
    async def kiss(self, ctx, user: discord.User):
        """Ok kiss"""
        response = await self.get_gif("kiss")
        if response is None:
            return await ctx.send("Something went wrong :c")
        custom_embed = discord.Embed(title="Kiss",
                                     description=f"{ctx.author.name} kisses {user.name}",
                                     color=discord.Colour.random())
        custom_embed.set_image(url=response)
        await ctx.send(embed=custom_embed)

    @commands.command()
    async def hug(self, ctx, user: discord.User):
        """Hugs someone"""
        response = await self.get_gif("hug")
        if response is None:
            return await ctx.send("Something went wrong :c")
        custom_embed = discord.Embed(title="Hug",
                                     description=f"{ctx.author.name} hugs {user.name}",
                                     color=discord.Colour.random())
        custom_embed.set_image(url=response)
        await ctx.send(embed=custom_embed)

    @commands.command()
    async def kill(self, ctx, user: discord.User):
        """Feels too angy? kill them"""
        response = await self.get_gif("kill")
        if response is None:
            return await ctx.send("Something went wrong :c")
        custom_embed = discord.Embed(title="Kill",
                                     description=f"{ctx.author.name} kills {user.name}",
                                     color=discord.Colour.random())
        custom_embed.set_image(url=response)
        await ctx.send(embed=custom_embed)

    @commands.command(aliases=["pet"])
    async def pat(self, ctx, user: discord.User):
        """Pat pat"""
        response = await self.get_gif("pat")
        if response is None:
            return await ctx.send("Something went wrong :c")
        custom_embed = discord.Embed(title="Pat",
                                     description=f"{ctx.author.name} pats {user.name}",
                                     color=discord.Colour.random())
        custom_embed.set_image(url=response)
        await ctx.send(embed=custom_embed)


async def setup(bot):
    await bot.add_cog(Action(bot))
