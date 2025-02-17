import discord
from discord.ext import commands
import json
from utils.logger import setup_logger

logger = setup_logger()

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setlogchannel')
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        """Set the channel for logging events"""
        try:
            # Verify it's a text channel
            if not isinstance(channel, discord.TextChannel):
                await ctx.send("❌ The specified channel must be a text channel!")
                return

            # Check if bot has required permissions in the channel
            bot_member = ctx.guild.me
            channel_perms = channel.permissions_for(bot_member)

            # Only check essential text channel permissions
            required_perms = {
                'view_channel': "View Channel",
                'send_messages': "Send Messages",
                'embed_links': "Embed Links"
            }

            missing_perms = [
                perm_name for perm_id, perm_name in required_perms.items()
                if not getattr(channel_perms, perm_id, False)
            ]

            if missing_perms:
                perms_list = ", ".join(missing_perms)
                await ctx.send(f"⚠️ I need the following permissions in {channel.mention}: {perms_list}\n"
                             f"Please grant these permissions and try again.")
                return

            # Update config
            with open('config.json', 'r') as f:
                config = json.load(f)

            config['log_channel'] = channel.id

            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)

            logger.info(f"Log channel set to: {channel.name}")

            embed = discord.Embed(
                title="✅ Log Channel Set",
                description=f"Successfully set {channel.mention} as the log channel.",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Next Steps",
                value="The bot will now log all server events to this channel.\n"
                      "Make sure to keep the bot's permissions unchanged for proper logging.",
                inline=False
            )
            await ctx.send(embed=embed)

            # Send a test message to the log channel
            test_embed = discord.Embed(
                title="🎉 Audit Log Channel Setup",
                description="This channel has been set as the audit log channel.\n"
                          "You will see server events logged here.",
                color=discord.Color.blue()
            )
            await channel.send(embed=test_embed)

        except Exception as e:
            logger.error(f"Error setting log channel: {e}")
            await ctx.send("❌ An error occurred while setting the log channel. Please try again.")

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot's latency"""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: `{latency}ms`",
            color=discord.Color.green() if latency < 200 else discord.Color.orange()
        )
        await ctx.send(embed=embed)

    @commands.command(name='commands')
    async def show_commands(self, ctx):
        """Show available commands"""
        embed = discord.Embed(
            title="Audit Log Bot Commands",
            description="Here are the available commands:",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="`!setlogchannel #channel`",
            value="Set the channel for logging events (Admin only)",
            inline=False
        )
        embed.add_field(
            name="`!ping`",
            value="Check bot's latency",
            inline=False
        )
        embed.add_field(
            name="`!commands`",
            value="Show this help message",
            inline=False
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CommandsCog(bot))