import requests
import nextcord
from nextcord.ext import commands
import json
import os, re
import logging
from nextcord.utils import find
from nextcord.ui import Button, View
from nextcord import *
from nextcord.guild import Guild
from nextcord.embeds import Embed
from nextcord.user import Colour
from nextcord.channel import TextChannel
from nextcord.channel import TextChannel as Channel
import sys
from webserver import keep_alive
from pathlib import Path
alice_root = Path(__file__).parent / "alice"
sys.path.append(alice_root.as_posix())
from pathlib import Path
import random


AUTH_TOKEN = str(os.environ['AUTH_TOKEN'])

DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
PREFIX = "+" or "@Kitten"
intents = Intents.all()
bot = commands.Bot(command_prefix=PREFIX, help_command=None, 
status=Status.idle, 
					activity=Streaming(name=f"+setup in {sum(guild.member_count for guild in bot.guilds)}", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"), intents=intents)



async def get_channel(message):
	with open("text_channels.json", "r") as file:
		guild = json.load(file)	
		key = str(message.guild.id)
		if key in guild:
			return guild[key]
		return None




@bot.event
async def on_ready():
	print("bot is online")


@bot.event
async def on_guild_join(guild):
	ch = [c for c in guild.text_channels if c.permissions_for(guild.me).send_messages][0]  # get first channel with speaking permissions
	print(ch)
	embed=nextcord.Embed(title=f"Thanks for Adding me to your server!\n\n I'm so glad to be in {guild.name}!\n \nTo talk with me, just have `@Kitten` in your message! \n \nTo setup a channel for me to talk in do:\n`+setup`", color=0x37393f)
	embed.set_author(name="Meow! I'm Kitten,")
	embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/889405771870257173/943436635343843328/cute_cat_4.jpeg")

	await ch.send(embed=embed)


def load_config():
	with open("text_channels.json", "r") as file:
		guild = json.load(file)
	return guild

def save_config(conf):
	with open("text_channels.json", "w") as file:
		json.dump(conf, file, indent=4)

@bot.command(name="ping")
async def ping(ctx: commands.Context):
	await ctx.send(f"the bot ping is currently: {round(bot.latency * 1000)}ms")

def replace_mention(word, members):
	if not word.startswith("<@"):
		return word
	word = word.replace("!", "")
	mbr_id = int(word[2:-1])
	mbrs = [b for g in bot.guilds for b in g.members]
	mbr = [m for m in mbrs if str(m.id) == str(mbr_id)][0]
	
	return mbr.name

@bot.command(pass_context = True)
async def whoami(ctx):
	if ctx.message.author.server_permissions.administrator:
		msg = "You're an admin {0.author.mention}".format(ctx.message)  
		await ctx.send(msg)
	else:
		msg = "You're an average joe {0.author.mention}".format(ctx.message)  
		await ctx.send(msg)

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx: commands.Context, *, args=''):
	channel: Channel = None
	removing: bool = False
	words = args.split()
	if words and words[0] == "remove":
		removing = True
		# drop first arg
		args = " ".join(words[1:])
	channel_match: re.Match = re.search(r"<#(?P<id>[0-9]+)>", args)
	if channel_match:
		guild_: Guild = ctx.guild
		channel = guild_.get_channel(int(channel_match.group("id")))
	guild: Guild = ctx.guild
	config = load_config()
	print(f"Setup command: {args=!r} {words=} {channel_match=} {channel=!r} {removing=!r}")
	def reply_maybe_embed(*args):
		status = [(int(sk), ctx.guild.get_channel(int(sk)),) for sk in ([config[str(guild.id)]] if str(guild.id) in config else [])]
		status_embed = Embed(
			title="Current Status", color=0xff7575,
			type='rich',
			description='\n'.join([f"{ch.mention}: installed" for chid, ch in status])
		)
		if status:
			return ctx.reply(*args, embed=status_embed)
		return ctx.reply(*args)
	#
	if channel is None:
		await reply_maybe_embed(
			"Hello there! \n"
			" - To setup the AI on a channel, do `+setup #channel`. \n"
			" - To remove the AI from a channel, do `+setup remove #channel`.")
		return
	if not removing:
		if guild.id in config:
			await reply_maybe_embed("Are you disabled?! You already have an AI channel set up!")
			return
		config[str(guild.id)] = channel.id
		save_config(config)
		await reply_maybe_embed(f"Alrighty! The channel {channel.mention} has been setup!")
		return
	# renoving
	if channel.guild.id == guild.id:
		if str(guild.id) in config:
			del config[str(guild.id)]
			save_config(config)
			await reply_maybe_embed(f"The channel {channel.mention} has been removed. I'll miss you! :(")
		else:
			await reply_maybe_embed(f"The channel {channel.mention} is not set up.")
	else:
		await reply_maybe_embed(f"The channel {channel.mention} is not in your guild.")
	return

@bot.command(name="print-message-to-console")
async def print_message(ctx, message):
	print(message)
	await ctx.send("message printed in console")

async def guild(ctx):
	guild = ctx.guild
	return guild

@bot.listen()
async def on_message(message):
	channel_id = await get_channel(message)
	bot_message = " ".join((replace_mention(word, message.guild.members) for word in message.content.split()))
	print(f"[{message.author.name}][{message.guild.name}]: {bot_message}")
	mention = f"<@!{bot.user.id}>"
	if bot.user == message.author:
		return
	if message.content and not message.content[0].isalnum():
		return
	if message.channel.id == channel_id or mention in message.content:
		print(message.content)
		url = "https://random-stuff-api.p.rapidapi.com/ai"

		querystring = {"msg": bot_message, "bot_name": "Kitten", "bot_gender": "Male", "bot_master": "Mikko#9600",
						"bot_age": "215", "bot_company": "Mikko Studios", "bot_location": "Mars", "bot_email": "idk",
						"bot_build": "Public", "bot_birth_year": "2056", "bot_birth_date": "69th Marsary, 2056",
						"bot_birth_place": "Mars", "bot_favorite_color": "Green", "name": message.author.name,
						"bot_favorite_book": "How to train a robot", "bot_favorit	e_band": "Python rock band",
						"bot_favorite_artist": "Pythoner", "id": message.author.id}
		headers = {
			'authorization': AUTH_TOKEN,
			'x-rapidapi-host': "random-stuff-api.p.rapidapi.com",
			'x-rapidapi-key': os.environ['RAPID_API_KEY']
		}
		response = """{
            "AIResponse": k.respond(
                bot_message, message.author.name
            )
        } """ ; response = requests.request("GET", url, headers=headers, params=querystring).json()
		print(response["AIResponse"])
		await message.reply(response["AIResponse"])
		await bot.process_commands(message)

keep_alive()

bot.run(DISCORD_BOT_TOKEN)