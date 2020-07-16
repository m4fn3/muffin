# import
from discord.ext import commands
import ast, asyncio, datetime, discord, io, json, os, psutil, subprocess, sys, time, traceback2


# class
class Dev(commands.Cog):

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        with open("./INFO.json") as F:
            info = json.load(F)
        self.info = info

    def save_roles(self):
        roles = {
            "ADMIN": self.bot.ADMIN,
            "Contributor": self.bot.Contributor,
            "BAN": self.bot.BAN
        }
        with open("./ROLE.json", 'w') as F:
            json.dump(roles, F, indent=2)

    def save_database(self):
        with open("./DATABASE.json", 'w') as F:
            json.dump(self.bot.database, F, indent=2)

    def execute_returns(self, body):
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])
        if isinstance(body[-1], ast.If):
            execute_returns(body[-1].body)
            execute_returns(body[-1].orelse)
        if isinstance(body[-1], ast.With):
            execute_returns(body[-1].body)

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
        self.save_database()

    async def update_status(self):
        game = discord.Game("{}help | {}servers\n[ http://mafu.cf/ ]".format(self.bot.PREFIX, str(len(self.bot.guilds))))
        await self.bot.change_presence(status=discord.Status.idle, activity=game)

    async def cog_before_invoke(self, ctx):
        if str(ctx.author.id) not in self.bot.database:
            await self.init_database(ctx)
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

    @commands.group()
    async def server(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("list | join | vc")

    @server.command(name="list")
    async def list_server(self, ctx):
        text = "サーバー一覧:"
        for i in self.bot.guilds:
            text += f"\n> **{i.name}**\n> ({i.id}) | {len(i.members)}"
        text += f"\n計: {len(self.bot.guilds)}サーバー"
        msg_obj = await ctx.send(text)
        await asyncio.sleep(30)
        await msg_obj.delete()

    @server.command(name="join")
    async def join_server(self, ctx, *, server_id):
        end_code = 0
        server_obj = None
        for i in self.bot.guilds:
            if str(i.id) == server_id:
                end_code = 1
                server_obj = i
                break
        if end_code == 0:
            await ctx.send("サーバーが見つかりませんでした")
        else:
            try:
                inv_list = await server_obj.invites()
            except:
                await ctx.send("既存のサーバー招待URLを取得する権限がありません.")
                inv_list = []
            if len(inv_list) != 0:
                await ctx.send("既存のサーバー招待URLを作成中です.")
                await ctx.send("サーバー招待URLをDMに送信します.")
                await ctx.author.send(inv_list[0])
            else:
                await ctx.send("新しいサーバー招待URLを作成中です.")
                inv_obj = None
                for text_ch in server_obj.text_channels:
                    try:
                        inv_obj = await text_ch.create_invite()
                    except:
                        continue
                    else:
                        break
                await ctx.send("サーバー招待URLをDMに送信します.")
                try:
                    await ctx.author.send(inv_obj)
                except:
                    await ctx.send("サーバー招待URLを作成する権限がありません.")

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
        self.save_database()

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
        self.save_roles()

    @admin.command(name="delete", aliases=["remove"])
    async def delete_admin(self, ctx, *, text):
        for target in ctx.message.mentions:
            if target.id not in self.bot.ADMIN:
                await ctx.send("このユーザーは管理者ではありません.")
            else:
                self.bot.ADMIN.remove(target.id)
                await ctx.send(f"<@{target.id}>さんが管理者から削除されました.")
        self.save_roles()

    @admin.command(name="list")
    async def list_admin(self, ctx):
        text = "管理者一覧:"
        for user in self.bot.ADMIN:
            text += "\n{0} ({0.id})".format(self.bot.get_user(user))
        await ctx.send(text)
        self.save_roles()

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
        self.save_roles()

    @ban.command(name="delete", aliases=["remove"])
    async def delete_ban(self, ctx, *, text):
        for target in ctx.message.mentions:
            if target.id not in self.bot.BAN:
                await ctx.send("このユーザーはBANされていません.")
            else:
                self.bot.BAN.remove(target.id)
                await ctx.send(f"<@{target.id}>さんがBANを解除されました.")
        self.save_roles()

    @ban.command(name="list")
    async def list_ban(self, ctx):
        text = "BANユーザー一覧:"
        for user in self.bot.BAN:
            text += "\n{0} ({0.id})".format(self.bot.get_user(user))
        await ctx.send(text)
        self.save_roles()

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
        self.save_roles()

    @contributor.command(name="delete", aliases=["remove"])
    async def delete_con(self, ctx, *, text):
        for target in ctx.message.mentions:
            if target.id not in self.bot.Contributor:
                await ctx.send("このユーザーは貢献者ではありません.")
            else:
                self.bot.Contributor.remove(target.id)
                await ctx.send(f"<@{target.id}>さんが貢献者ではなくなりました.")
        self.save_roles()

    @contributor.command(name="list")
    async def list_con(self, ctx):
        text = "貢献者一覧:"
        for user in self.bot.Contributor:
            text += "\n{0} ({0.id})".format(self.bot.get_user(user))
        await ctx.send(text)
        self.save_roles()

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
                    await music.leave_all(ctx)
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
                await music.leave_all(ctx)
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
        await music.leave_all(ctx)
        self.save_roles()
        self.save_database()
        await ctx.send(":closed_lock_with_key:BOTを再起動します.")
        python = sys.executable
        os.execl(python, python, * sys.argv)

    @system.command(aliases=["q"])
    async def quit(self, ctx):
        music = self.bot.get_cog("Music")
        await music.leave_all(ctx)
        self.save_roles()
        self.save_database()
        await ctx.send(":closed_lock_with_key:BOTを停止します.")
        sys.exit()

    @commands.command()
    async def exe(self, ctx, *, cmd):
        try:
            fn_name = "_eval_expr"
            cmd = cmd.strip("` ")
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
            body = f"async def {fn_name}():\n{cmd}"
            parsed = ast.parse(body)
            body = parsed.body[0].body
            self.execute_returns(body)
            env = {
                'bot': ctx.bot,
                'discord': discord,
                'commands': commands,
                'ctx': ctx,
                '__import__': __import__
            }
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            result = (await eval(f"{fn_name}()", env))
            await ctx.message.add_reaction("✅")
        except:
            await ctx.message.add_reaction("🚫")
            await ctx.send(f"{traceback2.format_exc()}")

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
