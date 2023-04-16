import os
import discord
from discord import Intents
from discord.ext import commands, tasks
import requests

TOKEN = 'MTA5Njk0ODE5NTA3NjA4MzcyMg.GKcyqK.F9oTOta4Mpq0UHQNnsYQ1tC6q1DCOMek2rv6mA'
COIN_ID = 'hobbes'  # Change this to the desired cryptocurrency ID from CoinGecko
REFRESH_INTERVAL = 60  # Refresh interval in seconds

intents = Intents.default()
intents.guilds = True
intents.messages = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

def get_crypto_data(coin_id):
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&community_data=false&developer_data=false&sparkline=false'
    response = requests.get(url)
    return response.json()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    update_crypto_data.start()

@tasks.loop(seconds=REFRESH_INTERVAL)
async def update_crypto_data():
    crypto_data = get_crypto_data(COIN_ID)
    guild = bot.guilds[0]

    # Get or create the "Crypto Info" category
    category = discord.utils.get(guild.categories, name="$HOBBES LIVE DATA")
    if not category:
        category = await guild.create_category(name="$HOBBES LIVE DATA")

    # Update the fully diluted valuation
    fdv = crypto_data['market_data']['fully_diluted_valuation']['usd']
    try:
        market_cap_channel = discord.utils.get(guild.voice_channels, name=f"MC: ${fdv:,.0f}")
        if market_cap_channel is None:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(connect=False)
            }
            market_cap_channel = await category.create_voice_channel(
                name=f"MC: ${fdv:,.0f}", overwrites=overwrites, reason="Creating channel for fully diluted valuation"
            )
        else:
            await market_cap_channel.edit(name=f"MC: ${fdv:,.0f}")
    except discord.errors.Forbidden:
        # handle the Forbidden error here
    except discord.errors.HTTPException:
        # handle the HTTP error here

    # Update the 24-hour trading volume
    volume = crypto_data['market_data']['total_volume']['usd']
    try:
        volume_channel = discord.utils.get(guild.voice_channels, name=f"24h Vol: ${volume:,.0f}")
        if volume_channel is None:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(connect=False)
            }
            volume_channel = await category.create_voice_channel(
                name=f"24h Vol: ${volume:,.0f}", overwrites=overwrites, reason="Creating channel for 24-hour trading volume"
            )
        else:
            await volume_channel.edit(name=f"24h Vol: ${volume:,.0f}")
    except discord.errors.Forbidden:
        # handle the Forbidden error here
    except discord.errors.HTTPException:
        # handle the HTTP error here

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

bot.run(TOKEN)



