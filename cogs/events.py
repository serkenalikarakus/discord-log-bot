import discord
from discord.ext import commands
import datetime
from utils.logger import setup_logger
from utils.config import load_config

logger = setup_logger()

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logger.info(f"Member joined: {member.name} ({member.id})")
        channel = self.get_log_channel(member.guild)
        if channel:
            embed = discord.Embed(
                title="Member Joined",
                description=f"{member.mention} joined the server",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"))
            embed.set_footer(text=f"Member ID: {member.id}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        logger.info(f"Member left: {member.name} ({member.id})")
        channel = self.get_log_channel(member.guild)
        if channel:
            embed = discord.Embed(
                title="Member Left",
                description=f"{member.name}#{member.discriminator} left the server",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Joined At", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S UTC"))
            embed.set_footer(text=f"Member ID: {member.id}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        logger.info(f"Message deleted in #{message.channel.name}")
        channel = self.get_log_channel(message.guild)
        if channel:
            embed = discord.Embed(
                title="Message Deleted",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            embed.add_field(name="Author", value=message.author.mention, inline=True)

            # Handle message content within Discord's limits
            if len(message.content) > 1024:
                content = message.content[:1021] + "..."
            else:
                content = message.content

            embed.add_field(name="Content", value=content or "*No content*", inline=False)
            embed.set_footer(text=f"Message ID: {message.id}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        logger.info(f"Channel created: {channel.name}")
        log_channel = self.get_log_channel(channel.guild)
        if log_channel:
            embed = discord.Embed(
                title="Channel Created",
                description=f"Channel {channel.mention} was created",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="Type", value=str(channel.type).title())
            embed.set_footer(text=f"Channel ID: {channel.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        logger.info(f"Channel deleted: {channel.name}")
        log_channel = self.get_log_channel(channel.guild)
        if log_channel:
            embed = discord.Embed(
                title="Channel Deleted",
                description=f"Channel **{channel.name}** was deleted",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="Type", value=str(channel.type).title())
            embed.set_footer(text=f"Channel ID: {channel.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        logger.info(f"Role created: {role.name}")
        channel = self.get_log_channel(role.guild)
        if channel:
            embed = discord.Embed(
                title="Role Created",
                description=f"Role **{role.name}** was created",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="Color", value=str(role.color))
            embed.add_field(name="Hoisted", value="Yes" if role.hoist else "No")
            embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No")
            embed.set_footer(text=f"Role ID: {role.id}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        logger.info(f"Role deleted: {role.name}")
        channel = self.get_log_channel(role.guild)
        if channel:
            embed = discord.Embed(
                title="Role Deleted",
                description=f"Role **{role.name}** was deleted",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="Color", value=str(role.color))
            embed.set_footer(text=f"Role ID: {role.id}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Log voice channel join/leave events"""
        logger.info(f"Voice state update for {member.name}")
        channel = self.get_log_channel(member.guild)
        if not channel:
            return

        # Handle joining voice channel
        if before.channel != after.channel:
            if after.channel:
                # Member joined a voice channel
                embed = discord.Embed(
                    title="Voice Channel Joined",
                    description=f"{member.mention} joined voice channel {after.channel.mention}",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"Member ID: {member.id}")
                await channel.send(embed=embed)

            elif before.channel:
                # Member left a voice channel
                embed = discord.Embed(
                    title="Voice Channel Left",
                    description=f"{member.mention} left voice channel {before.channel.mention}",
                    color=discord.Color.orange(),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"Member ID: {member.id}")
                await channel.send(embed=embed)

    def get_log_channel(self, guild):
        """Get the logging channel for the guild"""
        try:
            config = load_config()
            if not config:
                return None

            channel_id = config.get('log_channel')
            if not channel_id:
                return None

            channel = guild.get_channel(int(channel_id))
            if not channel:
                logger.warning(f"Could not find log channel with ID {channel_id}")
                return None

            # Check if bot has necessary permissions
            permissions = channel.permissions_for(guild.me)
            if not (permissions.send_messages and permissions.embed_links):
                logger.warning(f"Missing required permissions in log channel {channel.name}")
                return None

            return channel
        except Exception as e:
            logger.error(f"Error getting log channel: {e}")
            return None

async def setup(bot):
    await bot.add_cog(EventsCog(bot))