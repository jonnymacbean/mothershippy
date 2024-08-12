# Token provided either as environment variable "MOTHERSHIPPY_TOKEN" or provided in the "token" variable below
token = ''

#=====================================================================================

import discord, os
from discord import app_commands
from discord.ext import commands
from discord.utils import get

if token == '':
    try:
        token = os.environ['MOTHERSHIPPY_TOKEN']
    except:
        print('Please provide a token') # TODO: proper logging here
        exit

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
client.tree = tree

@client.event
async def on_ready():
    print(f'logged in as {client.user}')
    await client.tree.sync()

@client.tree.command(name="create_game",description="Create new channels to run a Mothership game in")
@app_commands.describe(name="The name of the game")
async def create_game(ctx, name: str):
    guild = ctx.guild
    print(guild)
    existing_category = discord.utils.get(guild.categories, name=name)
    if not existing_category:
        
        bot_role = get(guild.roles, name=guild.me.display_name) 
        print(bot_role)
		# Create roles
        player_role = await guild.create_role(name=f"mothership - {name} players")
        spectator_role = await guild.create_role(name=f"mothership - {name} spectators")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False, 
                connect=False
                ),
            player_role: discord.PermissionOverwrite(
                read_messages=True, 
                send_messages=True, 
                connect=True, 
                speak=True
                ),
            spectator_role: discord.PermissionOverwrite(
                read_messages=True, 
                send_messages=True, 
                connect=True, 
                speak=False
                )
        }
        await ctx.user.add_roles(player_role)
        new_category = await guild.create_category(name, overwrites=overwrites)

        # create text channels
        cards_channel = await new_category.create_text_channel("Player cards")
        text_channel = await new_category.create_text_channel("Game chat")
        warden_channel = await new_category.create_text_channel("Warden")
        await warden_channel.set_permissions(ctx.user, read_messages=True, send_messages=True)
        await warden_channel.set_permissions(player_role, view_channel=False)
        await warden_channel.set_permissions(spectator_role, view_channel=False)
        # create voice channel
        voice_channel = await new_category.create_voice_channel("Game voice")
        await ctx.response.send_message(f'"{name}" has been created with relevant channels')
    else:
        await ctx.response.send_message(f'Category "{name}" already exists, please choose a different name.')

"""
@client.tree.command(name="players",description="Add or remove players from the game")
@app_commands.describe(add="name of player to add",remove="name of player to remove")
async def players(ctx, add: str, remove: str):
    guild = ctx.guild
"""

client.run(token)
