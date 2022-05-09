import os
from datetime import datetime
from glob import glob
from os import getenv
from os.path import relpath
from traceback import format_exception

import asyncio
import aiohttp
import discord
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()

# FIXME: Cooldown mapping bugs out on help command


COMMANDS_FOLDER = r"commands/"

TOKEN = getenv("DISCORD_TOKEN")

fallback = os.urandom(32).hex()
prefixes = ["don."]

launch_time = int(datetime.now().timestamp())


def _prefix_callable(bot_, msg):
    bot_id = bot_.user.id
    prefixes.extend([f"<@!{bot_id}> ", f"<@{bot_id}> "])
    return prefixes


class DonBot(commands.Bot):
    def __init__(self):
        allowed_mention = discord.AllowedMentions(roles=False, everyone=False, users=True)
        intents = discord.Intents.all()
        super().__init__(command_prefix=_prefix_callable,
                         description="Bot made for G13",
                         allowed_mention=allowed_mention,
                         intents=intents)

    # async def get_prefix(self, msg):
    #     comp = re.compile("^(" + "|".join(map(re.escape, prefixes)) + ").*", flags=re.I)
    #     match = comp.match(msg.content)
    #     if match is not None:
    #         return match.group(1)
    #     return fallback

    async def load_commands(self):
        for file in glob(f"{COMMANDS_FOLDER}*.py"):
            module_name = relpath(file).replace("\\", '.').replace('/', '.')[:-3]
            await self.load_extension(module_name)
        await self.load_extension("jishaku")
        print("Module loaded")


class CustomHelpCommand(commands.MinimalHelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            "cooldown": commands.CooldownMapping.from_cooldown(1.0, 3.0, commands.BucketType.user)
        })

    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            # Ignore missing permission errors
            if isinstance(error.original, discord.HTTPException) and error.original.code == 50013:
                return
            await ctx.send(embed=discord.Embed(title="Error", description=error.original))

    async def send_pages(self) -> None:
        destination = self.get_destination()
        for page in self.paginator.pages:
            help_embed = discord.Embed(title="Help", description=page, color=discord.Colour.random())
            await destination.send(embed=help_embed)


bot = DonBot()


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to discord!")
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Activity(type=discord.ActivityType.listening,
                                                        name=f"don.help"))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.NotOwner):
        return await ctx.reply(error, mention_author=False)
    if isinstance(error, commands.errors.DisabledCommand):
        return await ctx.reply("This command is disabled or under maintenance", mention_author=False)
    if isinstance(error, commands.errors.CommandOnCooldown):
        return await ctx.reply(str(error), mention_author=False, delete_after=error.retry_after)
    if isinstance(error, commands.errors.UserNotFound):
        return await ctx.reply("User not found", mention_author=False)
    if isinstance(error, commands.errors.CommandNotFound) or hasattr(ctx.command, 'on_error'):
        return
    owner = await bot.fetch_user(436376194166816770)
    channel = await owner.create_dm()
    output = ''.join(format_exception(type(error), error, error.__traceback__))
    await channel.send(f"Uncaught error in channel <#{ctx.channel.id}> command `{ctx.command}`\n"
                       f"```py\n"
                       f"{output}```")


async def main():
    bot.help_command = CustomHelpCommand()
    await bot.load_commands()
    async with aiohttp.ClientSession() as session:
        bot.session = session
        await bot.start(TOKEN)


if __name__ == '__main__':
    asyncio.run(main())
