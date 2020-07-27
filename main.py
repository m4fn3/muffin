from discord.ext import commands, tasks
import asyncio, discord, time, json, logging, os, io, traceback2, signal, sys
import nest_asyncio
nest_asyncio.apply()

TOKEN = os.getenv("TOKEN")
with open("./INFO.json") as F:
    info = json.load(F)

logging.basicConfig(level=logging.INFO)


class Muffin(commands.Bot):

    def __init__(self, command_prefix):
        super().__init__(command_prefix)

        self.remove_command("help")

        for cog in info["COG"]:
            self.load_extension(cog)

        self.uptime = time.time()
        self.playlist = {}
        self.voice_status = {}
        self.voice_disconnected = []
        self.music_skipped = []
        self.wait_leave = []

        self.global_chat_log = {}
        self.PREFIX = info["PREFIX"]

        self.ADMIN = []
        self.BAN = []
        self.Contributor = []
        self.database = {}
        self.global_chat = {}
        self.api_index = 1

    async def on_ready(self):
        try:
            print(f"Logged in to {bot.user}")
            if self.user.id == 644065524879196193:
                await self.get_channel(info["ERROR_CHANNEL"]).send("Logged in")
            if not discord.opus.is_loaded():
                try:
                    discord.opus.load_opus("heroku-buildpack-libopus")
                except:
                    pass
            database_channel = self.get_channel(736538898116902925)
            database_msg = await database_channel.fetch_message(database_channel.last_message_id)
            database_file = database_msg.attachments[0]
            db_byte = await database_file.read()
            db_dict = json.loads(db_byte)
            self.ADMIN = db_dict["role"]["ADMIN"]
            self.BAN = db_dict["role"]["BAN"]
            self.Contributor = db_dict["role"]["Contributor"]
            self.database = db_dict["user"]
            self.global_chat = db_dict["global_chat"]
            self.api_index = db_dict["music"]
            self.save_database.start()
            loop = asyncio.get_event_loop()
            self.loop.add_signal_handler(signal.SIGTERM, lambda: loop.run_until_complete(self.on_sigterm()))
        except:
            print(traceback2.format_exc())

    async def on_message(self, message):
        if not self.is_ready():
            return
        elif message.author.bot:
            return
        elif message.guild is None:
            return await message.channel.send("muffin is __Only__ available on Servers!\nTo get started: http://mafu.cf/\nTo invite Bot: http://mafu.cf/muffin")
        #elif message.channel.id in self.global_chat["general"]:
        #    global_chat_cog = self.get_cog("GlobalChat")
        #    await global_chat_cog.on_global_message(message)
        else:
            await self.process_commands(message)

    async def on_sigterm(self):
        db_dict = {
            "user": self.database,
            "role": {
                "ADMIN": self.ADMIN,
                "BAN": self.BAN,
                "Contributor": self.Contributor
            },
            "global_chat": self.global_chat,
            "music": self.api_index
        }
        database_channel = self.get_channel(736538898116902925)
        db_bytes = json.dumps(db_dict, indent=2)
        await database_channel.send(file=discord.File(fp=io.StringIO(db_bytes), filename="database.json"))
        music = self.get_cog("Music")
        await music.leave_all()
        sys.exit()

    @tasks.loop(seconds=30.0)
    async def save_database(self):
        db_dict = {
            "user": self.database,
            "role": {
                "ADMIN": self.ADMIN,
                "BAN": self.BAN,
                "Contributor": self.Contributor
            },
            "global_chat": self.global_chat,
            "music": self.api_index
        }
        database_channel = self.get_channel(736538898116902925)
        db_bytes = json.dumps(db_dict, indent=2)
        await database_channel.send(file=discord.File(fp=io.StringIO(db_bytes), filename="database.json"))


if __name__ == '__main__':
    bot = Muffin(command_prefix=(info["PREFIX"]))
    bot.run(TOKEN)
