import discord
from discord.ext import commands, tasks
import os
import aiohttp
import json
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Bot setup with necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ERLC API configuration
ERLC_API_TOKEN = os.getenv('ERLC_TOKEN')
ERLC_SERVER_ID = os.getenv('ERLC_SERVER_ID')  # You'll need to set this in .env
api_base_url = "https://api.emergency-response.tech"

async def fetch_erlc_data(endpoint):
    """Generic function to fetch data from ERLC API"""
    headers = {'Authorization': ERLC_API_TOKEN}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_base_url}{endpoint}", headers=headers) as response:
            if response.status == 200:
                return await response.json()
            return None

# Event: When bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

# Command: Check player count
@bot.command()
async def players(ctx):
    data = await fetch_erlc_data(f"/servers/{ERLC_SERVER_ID}/players")
    if data:
        players_list = data.get('players', [])
        embed = discord.Embed(title="Server Players", color=discord.Color.blue())
        embed.add_field(name="Player Count", value=str(len(players_list)), inline=False)
        
        # List players if there are any
        if players_list:
            players_text = "\n".join([player['username'] for player in players_list[:20]])
            if len(players_list) > 20:
                players_text += f"\n...and {len(players_list) - 20} more"
            embed.add_field(name="Players", value=players_text, inline=False)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("Unable to fetch player count.")

# Command: Get recent logs
@bot.command()
async def logs(ctx, log_type="all", limit=10):
    """Get recent server logs. Types: all, join, leave, kill, cmd"""
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("You don't have permission to view logs!")
        return

    endpoint = f"/servers/{ERLC_SERVER_ID}/logs"
    data = await fetch_erlc_data(endpoint)
    
    if data:
        logs = data.get('logs', [])
        filtered_logs = []
        
        for log in logs:
            if log_type == "all" or log['type'].lower() == log_type.lower():
                filtered_logs.append(log)
                if len(filtered_logs) >= limit:
                    break

        if filtered_logs:
            embed = discord.Embed(title=f"Recent {log_type.upper()} Logs", color=discord.Color.blue())
            for log in filtered_logs:
                timestamp = datetime.fromtimestamp(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                embed.add_field(
                    name=f"{log['type']} - {timestamp}",
                    value=log['content'],
                    inline=False
                )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No {log_type} logs found.")
    else:
        await ctx.send("Unable to fetch logs.")

# Command: Start shift
@bot.command()
async def startshift(ctx):
    # TODO: Implement shift start logic
    await ctx.send(f"{ctx.author.name} has started their shift!")

# Command: End shift
@bot.command()
async def endshift(ctx):
    # TODO: Implement shift end logic
    await ctx.send(f"{ctx.author.name} has ended their shift!")

# Run the bot
if __name__ == "__main__":
    # Get tokens from environment variables
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    if None in [DISCORD_TOKEN, ERLC_API_TOKEN, ERLC_SERVER_ID]:
        print("Error: Missing required environment variables!")
    else:
        bot.run(DISCORD_TOKEN)
