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


if __name__ == '__main__':
    bot = Muffin(command_prefix=(info["PREFIX"]))
    bot.run(tokens["TOKEN"])
