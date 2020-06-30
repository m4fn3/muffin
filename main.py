# import
from discord.ext import commands
import json, logging
from developer import Dev
from music import Music
from game import Game
from other import Other

# define
with open("./INFO.json") as F:
    info = json.load(F)
with open("./TOKEN.json") as F:
    tokens = json.load(F)

# settings
bot = commands.Bot(command_prefix=(info["PREFIX"]))
bot.remove_command('help')
logging.basicConfig(level=logging.INFO)

bot.load_extension("developer")
bot.load_extension("music")
bot.load_extension("game")
bot.load_extension("other")

# Load
@bot.event
async def on_ready():
    print("Logged in to {}".format(bot.user))
    await bot.get_channel(info["ERROR_CHANNEL"]).send("on_ready()が呼び出されました.")

# run
bot.run(tokens["TOKEN"])
