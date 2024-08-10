import discord, os
from discord import app_commands
from discord.ext import commands

# Token provided either as environment variable "MOTHERSHIPPY_TOKEN" or provided in the "token" variable below
token = ''

if token == '':
	try:
		token = os.environ['MOTHERSHIPPY_TOKEN']
	except:
		print('Please provide a token') # TODO: proper logging here

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
    existing_category = discord.utils.get(guild.categories, name=name)
    if not existing_category:
        new_category = await guild.create_category(name)

		# Create roles
        player_role = await guild.create_role(name=f"{name} players")
        spectator_role = await guild.create_role(name=f"{name} spectators")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            player_role: discord.PermissionOverwrite(read_messages=True)
        }
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
            player_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            spectator_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        await ctx.user.add_roles(player_role)

        # create text channels
        cards_channel = await new_category.create_text_channel("Player cards", overwrites=overwrites)
        text_channel = await new_category.create_text_channel("Game chat", overwrites=overwrites)
        warden_channel = await new_category.create_text_channel("Warden")
        await warden_channel.set_permissions(ctx.user, read_messages=True, send_messages=True)
        # create voice channel
        game_voice_overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=False),
            player_role: discord.PermissionOverwrite(connect=True, speak=True),
			spectator_role: discord.PermissionOverwrite(connect=True, speak=False)
        }
        voice_channel = await new_category.create_voice_channel("Game voice", overwrites=game_voice_overwrites)
        await ctx.response.send_message(f'"{name}" has been created with relevant channels')
    else:
        await ctx.response.send_message(f'Category "{name}" already exists, please choose a different name.')
	

client.run(token)
