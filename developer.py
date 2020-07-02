# import
from discord.ext import commands
import ast, asyncio, datetime, discord, json, os, psutil, sys, time, traceback2


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

    def insert_returns(self, body):
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])
        if isinstance(body[-1], ast.If):
            insert_returns(body[-1].body)
            insert_returns(body[-1].orelse)
        if isinstance(body[-1], ast.With):
            insert_returns(body[-1].body)

    async def update_status(self):
        game = discord.Game("{}help | {}servers | v{} \n [ http://mafu.cf/ ]".format(self.info["PREFIX"],str(len(self.bot.guilds)),self.info["VERSION"]))
        await self.bot.change_presence(status=discord.Status.idle, activity=game)

    async def cog_before_invoke(self, ctx):
        if ctx.author.id not in self.bot.ADMIN:
            raise commands.CommandError("Developer-Admin-Error")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.update_status()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.get_channel(self.info["ERROR_CHANNEL"]).send("{}に参加しました.".format(guild.name))
        await self.update_status()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.get_channel(self.info["ERROR_CHANNEL"]).send("{}を退出しました.".format(guild.name))
        await self.update_status()

    @commands.Cog.listener()
    async def on_message(self, message):
        if "<@!644065524879196193>" in message.content:
            if str(message.guild.region) == "japan":
                embed = discord.Embed(title="使い方", color=0xffff99, url=self.info["WEB_COMMAND_URL_JA"])
                embed.add_field(name="公式サイトで詳しいコマンドの説明を確認してください!", value="[{0}]({0})".format(self.info["WEB_COMMAND_URL_JA"]), inline=False)
                embed.add_field(name="各種類のコマンドの一覧を表示するには:", value="```yaml\n{0}help music ... 音楽コマンド一覧\n{0}help game ... ゲームコマンド一覧\n{0}help other ... その他のコマンド一覧```".format(self.info["PREFIX"]), inline=False)
                embed.add_field(name="さらにmuffinについて知るには:", value="```fix\n{0}invite ... BOTの招待URLを送信します.\n{0}info ... BOTの情報を表示します.```".format(self.info["PREFIX"]), inline=False)
                embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="作成者: {} | [公式鯖リンク]({}) | [公式ウェブサイト]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL_JA"]))
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(title="Usage", color=0xffff99, url=self.info["WEB_COMMAND_URL"])
                embed.add_field(name="Please check commands details on Official WebSite!", value="[{0}]({0})".format(self.info["WEB_COMMAND_URL"]), inline=False)
                embed.add_field(name="To see each type of Commands:", value="```yaml\n{0}help music ... MusicCommands\n{0}help game ... GameCommands\n{0}help other ... OtherCommands```".format(self.info["PREFIX"]), inline=False)
                embed.add_field(name="Know more about muffin:", value="```fix\n{0}invite ... Send Invitation link.\n{0}info ... Show BOT information.```".format(self.info["PREFIX"]), inline=False)
                embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="Author: {} | [OfficialServer]({}) | [OfficialWebSite]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL_JA"]), inline=False)
                await message.channel.send(embed=embed)

    @commands.command()
    async def updatestatus(self, ctx):
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
            text += "\n> **{}**\n> ({}) | {}".format(i.name, i.id, len(i.members))
        text += "\n計: {}サーバー".format(len(self.bot.guilds))
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
            text += "\n> **{}** ({})\n> ({}) | {}".format(i.guild.name, len(i.channel.members), i.guild.id, len(i.guild.members))
        text += "\n計: {}サーバー".format(len(self.bot.voice_clients))
        await ctx.send(text)

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
                await ctx.send("<@{}>さんが管理者になりました.".format(target.id))
        self.save_roles()

    @admin.command(name="delete", aliases=["remove"])
    async def delete_admin(self, ctx, *, text):
        for target in ctx.message.mentions:
            if target.id not in self.bot.ADMIN:
                await ctx.send("このユーザーは管理者ではありません.")
            else:
                self.bot.ADMIN.remove(target.id)
                await ctx.send("<@{}>さんが管理者から削除されました.".format(target.id))
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
                await ctx.send("<@{}>がBANされました.".format(target.id))
        self.save_roles()

    @ban.command(name="delete", aliases=["remove"])
    async def delete_ban(self, ctx, *, text):
        for target in ctx.message.mentions:
            if target.id not in self.bot.BAN:
                await ctx.send("このユーザーはBANされていません.")
            else:
                self.bot.BAN.remove(target.id)
                await ctx.send("<@{}>さんがBANを解除されました.".format(target.id))
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
                await ctx.send("<@{}>が貢献者になりました.".format(target.id))
        self.save_roles()

    @contributor.command(name="delete", aliases=["remove"])
    async def delete_con(self, ctx, *, text):
        for target in ctx.message.mentions:
            if target.id not in self.bot.Contributor:
                await ctx.send("このユーザーは貢献者ではありません.")
            else:
                self.bot.Contributor.remove(target.id)
                await ctx.send("<@{}>さんが貢献者ではなくなりました.".format(target.id))
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
        EXTENSION_LIST = ["developer", "music", "game", "other"]
        if text in EXTENSION_LIST:
            try:
                if text == "music":
                    music = self.bot.get_cog("Music")
                    await music.leave_all(ctx)
                self.bot.unload_extension(text)
                self.bot.load_extension(text)
            except:
                await ctx.send("{}の再読み込みに失敗しました\n{}.".format(text, traceback2.format_exc()))
            else:
                await ctx.send("{}の再読み込みに成功しました.".format(text))
        else:
            await ctx.send("存在しない名前です.")

    @system.command(aliases=["l"])
    async def load(self, ctx, text):
        EXTENSION_LIST = ["developer", "music", "game", "other"]
        if text in EXTENSION_LIST:
            try:
                self.bot.load_extension(text)
            except:
                await ctx.send("{}の読み込みに失敗しました\n{}.".format(text,traceback2.format_exc()))
            else:
                await ctx.send("{}の読み込みに成功しました.".format(text))
        else:
            await ctx.send("存在しない名前です.")

    @system.command(aliases=["u"])
    async def unload(self, ctx, text):
        EXTENSION_LIST = ["developer", "music", "game", "other"]
        if text in EXTENSION_LIST:
            try:
                music = self.bot.get_cog("Music")
                await music.leave_all(ctx)
                self.bot.unload_extension(text)
            except:
                await ctx.send("{}の切り離しに失敗しました\n{}.".format(text,traceback2.format_exc()))
            else:
                await ctx.send("{}の切り離しに成功しました.".format(text))
        else:
            await ctx.send("存在しない名前です.")

    @system.command(aliases=["re"])
    async def restart(self, ctx):
        music = self.bot.get_cog("Music")
        await music.leave_all(ctx)
        self.save_roles()
        await ctx.send(":closed_lock_with_key:BOTを再起動します.")
        python = sys.executable
        os.execl(python, python, * sys.argv)

    @system.command(aliases=["q"])
    async def quit(self, ctx):
        music = self.bot.get_cog("Music")
        await music.leave_all(ctx)
        self.save_roles()
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
            self.insert_returns(body)
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
            await ctx.send("{}".format(traceback2.format_exc()))

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


def setup(bot):
    bot.add_cog(Dev(bot))
