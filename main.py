# import
from discord.ext import commands
import time, json, logging

# define
with open("./INFO.json") as F:
    info = json.load(F)
with open("./TOKEN.json") as F:
    tokens = json.load(F)

logging.basicConfig(level=logging.INFO)


class Muffin(commands.Bot):

    def __init__(self, command_prefix):
        super().__init__(command_prefix)

        self.remove_command("help")

        self.load_extension("developer")
        self.load_extension("music")
        self.load_extension("game")
        self.load_extension("other")
        self.load_extension("setting")

        self.uptime = time.time()
        self.playlist = {}
        self.voice_status = {}
        self.voice_disconnected = []
        self.music_skipped = []
        with open("./ROLE.json") as F:
            roles = json.load(F)
        self.ADMIN = roles["ADMIN"]
        self.Contributor = roles["Contributor"]
        self.BAN = roles["BAN"]
        with open("./DATABASE.json") as F:
            database = json.load(F)
        self.database = database
        self.PREFIX = info["PREFIX"]

    async def on_ready(self):
        print(f"Logged in to {bot.user}")
        if self.user.id == 644065524879196193:
            await self.get_channel(info["ERROR_CHANNEL"]).send("Logged in")

    async def on_message(self, message):
        if message.author.bot:
            raise commands.CommandError("From Bot")
        elif message.guild is None:
            await message.channel.send("muffin is __Only__ available on Servers!\nTo get started: http://mafu.cf/\nTo invite Bot: http://mafu.cf/muffin")
            raise commands.CommandError("Not Available On DM")
        else:
            await self.process_commands(message)


if __name__ == '__main__':
    bot = Muffin(command_prefix=(info["PREFIX"]))
    bot.run(tokens["TOKEN"])
