import discord
from discord.ext import commands
import json
import logging
from utils.logger import setup_logger
import os
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logger = setup_logger()

# Initialize bot with all intents
intents = discord.Intents.all()  # Enable all intents since we need comprehensive event tracking
bot = commands.Bot(command_prefix=os.getenv('prefix'), intents=intents)

# Load cogs
async def load_extensions():
    await bot.load_extension('cogs.events')
    await bot.load_extension('cogs.commands')

@bot.event
async def on_ready():
    logger.info(f'Bot is ready! Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="Gözüm kütüklerinizde!👀"
    ))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("Command not found!")
    elif isinstance(error, commands.errors.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    else:
        logger.error(f"An error occurred: {error}")
        await ctx.send("An error occurred while executing the command.")

async def main():
    token = os.environ.get('DISCORD_BOT_TOKEN')
    if not token:
        logger.error("No Discord bot token found in environment variables!")
        raise ValueError("DISCORD_BOT_TOKEN environment variable is not set")

    async with bot:
        await load_extensions()
        await bot.start(token)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())