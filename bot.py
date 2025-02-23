import discord
from discord.ext import commands
import logging
from utils.logger import setup_logger
from utils.config import CONFIG  # Import CONFIG from config.py

# Setup logging
logger = setup_logger()

# Initialize bot with all intents
intents = discord.Intents.all()  # Enable all intents since we need comprehensive event tracking
bot = commands.Bot(command_prefix=CONFIG["prefix"], intents=intents)  # Use PREFIX from CONFIG

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
    token = CONFIG["TOKEN"]  # Use TOKEN from CONFIG
    if not token:
        logger.error("No Discord bot token found in configuration!")
        raise ValueError("DISCORD_TOKEN is missing in config.py")

    async with bot:
        await load_extensions()
        await bot.start(token)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
