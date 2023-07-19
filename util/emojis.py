'''
Utility functions for handling of emoji synchronization across guilds
'''

import discord
from .log import Log

HUB_SERVER_ID = 996607138803748954

async def sync_add(cache: set, bot: discord.Bot, emoji: discord.Emoji):
    for guild in bot.guilds:
        # Check if this emoji already exists
        guild_emojis = await guild.fetch_emojis()
        exists = False
        for guild_emoji in guild_emojis:
            if guild_emoji.name == emoji.name:
                exists = True
                break

        # If the emoji exists, we can skip creation
        if exists:
            continue

        try:
            # Create emoji and add it to the cache
            created_emoji = await guild.create_custom_emoji(name=emoji.name, image=await emoji.read())
            cache.add(created_emoji)

            # Send confirmation to logs channel 
            logs = discord.utils.get(guild.channels, name="logs")
            if not logs:
                Log.error(f'No logs channel in {guild.name}')
            elif logs.guild.id != HUB_SERVER_ID:
                await logs.send(content=f'Emoji: {emoji.name} was added')

            Log.ok(f'Emoji: {emoji.name} successfully added in {guild.name}')
        except:
            Log.warning(f'Could not create emoji {emoji.name} in {guild.name}')
            continue

async def sync_delete(cache: set, bot: discord.Bot, emoji: discord.Emoji):
    for guild in bot.guilds:
        guild_emojis = await guild.fetch_emojis()
        del_emoji = None

        # Check if the guild contains an emoji that matches this one
        for guild_emoji in guild_emojis:
            if guild_emoji.name == emoji.name:
                del_emoji = guild_emoji
                break

        if del_emoji:
            # Delete the emoji in the server if possible
            # Could be forbidden to delete the emoji or get HTTP Exception
            try:
                # Add the emoji object to the cache
                await del_emoji.delete()
                cache.add(del_emoji)

                # Send confirmation to logs channel                
                logs = discord.utils.get(guild.channels, name="logs")
                if not logs:
                    Log.error(f'No logs channel in {guild.name}')
                elif logs.guild.id != HUB_SERVER_ID:
                    await logs.send(content=f'Emoji {emoji.name} was deleted')
                Log.ok(f'Emoji: {emoji.name} in {guild.name} successfully deleted')
            except:
                Log.warning(f'Could not delete emoji {emoji.name} in {guild.name}')
                continue

async def sync_name(cache: set, bot: discord.Bot, old_emoji: discord.Emoji, new_emoji: discord.Emoji):
    for guild in bot.guilds:

        # Check the guild for an emoji with the same name
        guild_emojis = await guild.fetch_emojis()
        for emoji in guild_emojis:

            # If the name matches, update it and move on to the next guild
            if emoji.name == old_emoji.name:
                # Add the emoji object to the cache
                await emoji.edit(name=new_emoji.name)
                cache.add(old_emoji)

                # Send confirmation to logs channel
                logs = discord.utils.get(guild.channels, name="logs")
                if not logs:
                    Log.error(f'No logs channel in {guild.name}')
                elif logs.guild.id != HUB_SERVER_ID:
                    await logs.send(content=f'Emoji: {old_emoji.name} was renamed to {new_emoji.name}')

                Log.ok(f'Updated emoji name {old_emoji.name} to {new_emoji.name} in guild {guild.id}')
                break
