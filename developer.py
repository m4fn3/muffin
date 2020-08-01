# import
from discord.ext import commands
from contextlib import redirect_stdout
import ast, asyncio, datetime, discord, io, json, os, psutil, subprocess, sys, textwrap, time, traceback2


# class
class Dev(commands.Cog):

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        with open("./INFO.json") as F:
            info = json.load(F)
        self.info = info
        self._last_result = None

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    async def save_database(self):
        db_dict = {
            "user": self.bot.database,
            "role": {
                "ADMIN": self.bot.ADMIN,
                "BAN": self.bot.BAN,
                "Contributor": self.bot.Contributor
            },
            "global_chat": self.bot.global_chat,
            "system": {
                "api_index": self.bot.api_index,
                "maintenance": self.bot.maintenance
            }
        }
        database_channel = self.bot.get_channel(736538898116902925)
        db_bytes = json.dumps(db_dict, indent=2)
        await database_channel.send(file=discord.File(fp=io.StringIO(db_bytes), filename="database.json"))

    async def init_database(self, ctx):
        self.bot.database[str(ctx.author.id)] = {
            "language": 0,
            "shadowchoice": {
                "best_score": 30.00,
                "single": {
                    "all_matches": 0,
                    "win_matches": 0
                },
                "multi": {
                    "all_matches": 0,
                    "win_matches": 0
                }
            },
            "music": {
                "play_message": True
            }
        }
        embed = discord.Embed(title=f"Welcome to muffin {len(self.bot.database)}th user!", description=f"<:muffin:731764451073720361> https://mafu.cf/\n<:help:731757723422556201>{self.bot.PREFIX}help")
        embed.add_field(name="Languages", value=":flag_jp:日本語 ... {0}lang ja\n:flag_us:English ... {0}lang en".format(self.bot.PREFIX))
        embed.add_field(name="Support", value=f"<:discord:731764171607375905> http://discord.gg/RbzSSrw\n{self.info['AUTHOR']}", inline=False)
        await ctx.send(embed=embed)
        await ctx.send(ctx.author.mention)

    async def update_status(self):
        game = discord.Game("{}help | {}servers\n[ http://mafu.cf/ ]".format(self.bot.PREFIX, str(len(self.bot.guilds))))
        await self.bot.change_presence(status=discord.Status.idle, activity=game)

    async def cog_before_invoke(self, ctx):
        if ctx.author.id not in self.bot.ADMIN:
            raise commands.CommandError("Developer-Admin-Error")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.update_status()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.get_channel(self.info["ERROR_CHANNEL"]).send(f"{guild.name}に参加しました.")
        await self.update_status()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.get_channel(self.info["ERROR_CHANNEL"]).send(f"{guild.name}を退出しました.")
        await self.update_status()

    @commands.Cog.listener()
    async def on_message(self, message):
        if "<@!644065524879196193>" in message.content:
            other = self.bot.get_cog("Other")
            ctx = await self.bot.get_context(message)
            await other.send_text(ctx, "HELP")

    @commands.command()
    async def apply_status(self, ctx):
        await self.update_status()
        await ctx.send(":white_check_mark:ステータスを更新しました.")

    @commands.group(aliases=["mt"])
    async def maintenance(self, ctx):
        if ctx.invoked_subcommand is None:
            context_msg = "有効" if ctx.bot.maintenance else "無効"
            await ctx.send(f"メンテナンスモードは{context_msg}です.")

    @maintenance.command(name="on")
    async def maintenance_on(self, ctx):
        if self.bot.maintenance:
            await ctx.send("メンテナンスモードは既に有効です")
        else:
            self.bot.maintenance = True
            await self.save_database()
            await ctx.send("メンテナンスモードを有効にしました")

    @maintenance.command(name="off")
    async def maintenance_off(self, ctx):
        if self.bot.maintenance:
            self.bot.maintenance = False
            await self.save_database()
            await ctx.send("メンテナンスモードを無効にしました")
        else:
            await ctx.send("メンテナンスモードはすでに無効です")

    @commands.group()
    async def server(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("server vc")

    @server.command()
    async def vc(self, ctx):
        text = "vc接続中のサーバー:"
        for i in self.bot.voice_clients:
            text += f"\n> **{i.guild.name}** ({len(i.channel.members)})\n> ({i.guild.id}) | {len(i.guild.members)}"
        text += f"\n計: {len(self.bot.voice_clients)}サーバー"
        await ctx.send(text)

    @commands.group(aliases=["db"])
    async def database(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("delete <@user>")

    @database.command(name="delete", aliases=["remove"])
    async def delete_database(self, ctx, *, text):
        for target in ctx.message.mentions:
            if str(target.id) not in self.bot.database:
                await ctx.send("このユーザーは登録されていません.")
            else:
                self.bot.database.pop(str(target.id))
                await ctx.send(f"<@{target.id}>さんをデータベースから削除されました.")
        await self.save_database()

    @commands.group()
    async def admin(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("add <@user> | delete <@user> | list ")

    @admin.command(name="add")
    async def add_admin(self, ctx, *, text):
        for target in ctx.message.mentions:
            if target.id in self.bot.ADMIN:
                await ctx.send("このユーザーは既に管理者です.")
            else:
                self.bot.ADMIN.append(target.id)
                await ctx.send(f"<@{target.id}>さんが管理者になりました.")
        await self.save_database()

    @admin.command(name="delete", aliases=["remove"])
    async def delete_admin(self, ctx, *, text):
        for target in ctx.message.mentions:
            if target.id not in self.bot.ADMIN:
                await ctx.send("このユーザーは管理者ではありません.")
            else:
                self.bot.ADMIN.remove(target.id)
                await ctx.send(f"<@{target.id}>さんが管理者から削除されました.")
        await self.save_database()

    @admin.command(name="list")
    async def list_admin(self, ctx):
        text = "管理者一覧:"
        for user in self.bot.ADMIN:
            text += "\n{0} ({0.id})".format(self.bot.get_user(user))
        await ctx.send(text)
        await self.save_database()

    @commands.group()
    async def ban(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("add <@user> | delete <@user> | list ")

    @ban.command(name="add")
    async def add_ban(self, ctx, *, text):
        for target in ctx.message.mentions:
            if target.id in self.bot.BAN:
                await ctx.send("このユーザーはすでにBANされています.")
            else:
                self.bot.BAN.append(target.id)
                await ctx.send(f"<@{target.id}>がBANされました.")
        await self.save_database()

    @ban.command(name="delete", aliases=["remove"])
    async def delete_ban(self, ctx, *, text):
        for target in ctx.message.mentions:
            if target.id not in self.bot.BAN:
                await ctx.send("このユーザーはBANされていません.")
            else:
                self.bot.BAN.remove(target.id)
                await ctx.send(f"<@{target.id}>さんがBANを解除されました.")
        await self.save_database()

    @ban.command(name="list")
    async def list_ban(self, ctx):
        text = "BANユーザー一覧:"
        for user in self.bot.BAN:
            text += "\n{0} ({0.id})".format(self.bot.get_user(user))
        await ctx.send(text)
        await self.save_database()

    @commands.group(aliases=["con"])
    async def contributor(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("add <@user> | delete <@user> | list ")

    @contributor.command(name="add")
    async def add_con(self, ctx, *, text):
        for target in ctx.message.mentions:
            if target.id in self.bot.Contributor:
                await ctx.send("このユーザーはすでに貢献者されています.")
            else:
                self.bot.Contributor.append(target.id)
                await ctx.send(f"<@{target.id}>が貢献者になりました.")
        await self.save_database()

    @contributor.command(name="delete", aliases=["remove"])
    async def delete_con(self, ctx, *, text):
        for target in ctx.message.mentions:
            if target.id not in self.bot.Contributor:
                await ctx.send("このユーザーは貢献者ではありません.")
            else:
                self.bot.Contributor.remove(target.id)
                await ctx.send(f"<@{target.id}>さんが貢献者ではなくなりました.")
        await self.save_database()

    @contributor.command(name="list")
    async def list_con(self, ctx):
        text = "貢献者一覧:"
        for user in self.bot.Contributor:
            text += "\n{0} ({0.id})".format(self.bot.get_user(user))
        await ctx.send(text)
        await self.save_database()

    @commands.group(aliases=["sys"])
    async def system(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("reload <Cog> | restart | quit")

    @system.command(aliases=["rl"])
    async def reload(self, ctx, text):
        if text in self.info["COG"]:
            try:
                if text == "music":
                    music = self.bot.get_cog("Music")
                    await music.leave_all()
                self.bot.reload_extension(text)
            except:
                await ctx.send(f"{text}の再読み込みに失敗しました\n{traceback2.format_exc()}.")
            else:
                await ctx.send(f"{text}の再読み込みに成功しました.")
        else:
            await ctx.send("存在しない名前です.")

    @system.command(aliases=["l"])
    async def load(self, ctx, text):
        if text in self.info["COG"]:
            try:
                self.bot.load_extension(text)
            except:
                await ctx.send(f"{text}の読み込みに失敗しました\n{traceback2.format_exc()}.")
            else:
                await ctx.send(f"{text}の読み込みに成功しました.")
        else:
            await ctx.send("存在しない名前です.")

    @system.command(aliases=["u"])
    async def unload(self, ctx, text):
        if text in self.info["COG"]:
            try:
                music = self.bot.get_cog("Music")
                await music.leave_all()
                self.bot.unload_extension(text)
            except:
                await ctx.send(f"{text}の切り離しに失敗しました\n{traceback2.format_exc()}.")
            else:
                await ctx.send(f"{text}の切り離しに成功しました.")
        else:
            await ctx.send("存在しない名前です.")

    @system.command(aliases=["re"])
    async def restart(self, ctx):
        music = self.bot.get_cog("Music")
        await music.leave_all()
        await self.save_database()
        await ctx.send(":closed_lock_with_key:BOTを再起動します.")
        python = sys.executable
        os.execl(python, python, * sys.argv)

    @system.command(aliases=["q"])
    async def quit(self, ctx):
        music = self.bot.get_cog("Music")
        await music.leave_all()
        await self.save_database()
        await ctx.send(":closed_lock_with_key:BOTを停止します.")
        sys.exit()

    @commands.command()
    async def exe(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback2.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.command(aliases=["pr"])
    async def process(self, ctx):
        td = datetime.timedelta(seconds=int(time.time() - self.bot.uptime))
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        d = td.days
        uptime = f"{d}d {h}h {m}m {s}s"
        cpu_per = psutil.cpu_percent()
        mem_total = psutil.virtual_memory().total / 10**9
        mem_used = psutil.virtual_memory().used / 10**9
        mem_per = psutil.virtual_memory().percent
        swap_total = psutil.swap_memory().total / 10**9
        swap_used = psutil.swap_memory().used / 10**9
        swap_per = psutil.swap_memory().percent
        guilds = len(self.bot.guilds)
        users = len(self.bot.users)
        vcs = len(self.bot.voice_clients)
        text_channels = 0
        voice_channels = 0
        for channel in self.bot.get_all_channels():
            if isinstance(channel, discord.TextChannel):
                text_channels += 1
            elif isinstance(channel, discord.VoiceChannel):
                voice_channels += 1
        latency = self.bot.latency
        embed = discord.Embed(title="Process")
        embed.add_field(name="Server", value=f"```yaml\nCPU: [{cpu_per}%]\nMemory:[{mem_per}%] {mem_used:.2f}GiB / {mem_total:.2f}GiB\nSwap: [{swap_per}%] {swap_used:.2f}GiB / {swap_total:.2f}GiB\n```", inline=False)
        embed.add_field(name="Discord", value=f"```yaml\nServers:{guilds}\nTextChannels:{text_channels}\nVoiceChannels:{voice_channels}\nUsers:{users}\nConnectedVC:{vcs}```", inline=False)
        embed.add_field(name="Run", value=f"```yaml\nUptime: {uptime}\nLatency: {latency:.2f}[s]\n```")
        await ctx.send(embed=embed)

    @commands.command()
    async def cmd(self, ctx, *, text):
        msg = ""
        try:
            output = await self.run_subprocess(text, loop=self.bot.loop)
            for i in range(len(output)):
                msg += output[i]
            await ctx.send(msg)
        except:
            await ctx.send(file=discord.File(fp=io.StringIO(msg), filename="output.txt"))

    async def run_subprocess(self, cmd, loop=None):
        loop = loop or asyncio.get_event_loop()
        try:
            process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except NotImplementedError:
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) as process:
                try:
                    result = await loop.run_in_executor(None, process.communicate)
                except Exception:  # muh pycodestyle
                    def kill():
                        process.kill()
                        process.wait()
                    await loop.run_in_executor(None, kill)
                    raise
        else:
            result = await process.communicate()

        return [res.decode('utf-8') for res in result]


def setup(bot):
    bot.add_cog(Dev(bot))
