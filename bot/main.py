@tasks.loop(seconds=28000)  # Refresh every eight hour
async def refresh_cache_fault():
    guild = bot.get_guild(guild_id)  # Assuming guild_id is globally set
    if guild is None:
        print('Guild not found. Cannot refresh cache.')
        return

    messages = []
    included_channels = [1113421046029242381, 1113429363950616586, 1113495131841110126]  # Add the IDs of channels to include
    max_messages = 50  # Adjust this to the number of messages you want to cache

    try:
        # Iterate through only the specified channels in the guild
        for channel_id in included_channels:
            channel = guild.get_channel(channel_id)
            if channel is None:
                print(f"Channel with ID {channel_id} not found.")
                continue

            # Ensure the bot has permission to read messages in the channel
            collected = 0  # Track the number of messages containing the phrase
            async for message in channel.history(limit=None):  # No limit on fetching messages
                if 'is it even my fault' in message.content.lower():
                    messages.append((channel.id, message.content))  # Store both channel ID and message content
                    collected += 1

                # Stop if we've collected the desired number of messages
                if collected >= max_messages:
                    break

            if collected >= max_messages:
                break

        # Cache the collected messages and update the timestamp
        cache_fault['messages'] = messages
        cache_fault['timestamp'] = time.time()
        print('Cache refreshed for specified channels.')
    except Exception as e:
        print(f'Error refreshing cache: {e}')
