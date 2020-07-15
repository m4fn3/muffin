# import
from discord.ext import commands
from matplotlib import colors
import aiohttp, asyncio, datetime, discord, io, json, os, pprint, psutil, re, sys, time, urllib, traceback2, webcolors
from identifier import *


class Other(commands.Cog):

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        with open("./INFO.json") as F:
            info = json.load(F)
        self.info = info
        self.user_match = "(?P<userid>[0-9]{18})"
        self.invite_match = "http(s)?://((ptb.|canary.)?discord(app)?.com/invite/|discord.gg/)(?P<invitecode>[a-zA-Z0-9_]{3,})"
        self.invite_match2 = "(?P<invitecode>[a-zA-Z0-9_]{3,})"
        self.message_match = "http(s)?://(ptb.|canary.)?discord(app)?.com/channels/(?P<guild>[0-9]{18})/(?P<channel>[0-9]{18})/(?P<message>[0-9]{18})"
        self.message_match2 = "(?P<message>[0-9]{18}"
        self.color_match = "(?P<color>[0-9a-fA-F]{6})"

    def save_database(self):
        with open("./DATABASE.json", 'w') as F:
            json.dump(self.bot.database, F, indent=2)

    def hex_to_rgb(self, hex_code):
        hlen = len(hex_code)
        return tuple(int(hex_code[i:i + hlen // 3], 16) for i in range(0, hlen, hlen // 3))

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
        embed = discord.Embed(title=f"Welcome to muffin {len(self.bot.database)}th user!",
                              description=f"<:muffin:731764451073720361> https://mafu.cf/\n<:help:731757723422556201>{self.bot.PREFIX}help")
        embed.add_field(name="Languages",
                        value=":flag_jp:日本語 ... {0}lang ja\n:flag_us:English ... {0}lang en".format(self.bot.PREFIX))
        embed.add_field(name="Support",
                        value=f"<:discord:731764171607375905> http://discord.gg/RbzSSrw\n{self.info['AUTHOR']}",
                        inline=False)
        await ctx.send(embed=embed)
        await ctx.send(ctx.author.mention)
        self.save_database()

    async def cog_command_error(self, ctx, error):
        """
        エラーが発生した時
        :param ctx: Context
        :param error: Error
        :return:
        """
        if isinstance(error, commands.MissingRequiredArgument):
            await self.send_text(ctx, "WRONG_COMMAND")
        elif isinstance(error, commands.errors.CommandNotFound):
            return
        elif isinstance(error, commands.errors.CommandError):
            return
        else:
            await self.send_text(ctx, "UNKNOWN_ERROR")
            await self.report_error(ctx, "on_command_error", str(error))

    async def cog_before_invoke(self, ctx):
        if str(ctx.author.id) not in self.bot.database:
            await self.init_database(ctx)
        if ctx.author.id in self.bot.BAN:
            await self.send_text(ctx, "YOUR_ACCOUNT_BANNED")
            raise commands.CommandError("Your Account Banned")

    async def send_text(self, ctx, code, arg1=None, arg2=None):
        lang = get_language(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        embed: discord.Embed
        if code == "INVALID_STRING":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(":warning:`不正な文字列です.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(":warning:`Invalid string.`")
        elif code == "TRANS_OVER_2000":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(":warning:`文字列が2000文字を超えるため翻訳結果を表示できませんでした.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(":warning:️`The translation result could not be displayed because the character string exceeds 2000 characters.")
        elif code == "WRONG_LANG_CODE":
            if lang == LanguageCode.JAPANESE:
                return await ctx.send(f":warning:`言語コードが間違っています. `{self.bot.PREFIX}tr_lg` で対応可能な言語コード一覧を確認できます.`")
            elif lang == LanguageCode.ENGLISH:
                return await ctx.send(f":warning:`Wrong lanuage code. Please send `{self.bot.PREFIX}tr_lg` to see list of avaiable language codes.`")
        elif code == "INVALID_ID":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(f":warning:`{arg1}は間違ったユーザーIDです.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(f":warning:`{arg1} is invalid`")
        elif code == "PLS_SPECIFY_WITH_ID_OR_MENTION":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(":warning:`メンションまたはユーザーIDで情報を表示するユーザーを指定してください.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(":warning:️`Please specify the user to display information by mention or user ID.`")
        elif code == "INVALID_LINK":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(f":warning:`{arg1}は間違った招待リンクです.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(f":warning:`{arg1} is invalid invitation link.`")
        elif code == "INVALID_MESSAGE":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(f":warning:`{arg1}は無効なメッセージリンクです.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(f":warning:`{arg1} is invalid message.`")
        elif code == "CANNOT_GET_CUZ_ANOTHER_SERVER":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(f":warning:`他のサーバーのメッセージであるため,取得できません.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(f":warning:`Cannot get because it is a message from another server.`")
        elif code == "YOUR_ACCOUNT_BANNED":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(":warning:`あなたはBANされているため,使用できません.\n異議申し立ては公式サーバーにてお願いします.`")
                raise commands.CommandError("Your Account Banned")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(
                    ":warning:`You cannnot use because you are banned.\nFor objection please use Official Server.`")
                raise commands.CommandError("Your Account Banned")
        elif code == "WRONG_HEX_CODE":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(f":warning:`間違った16進数カラーコードです.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(f":warning:`Wrong hexadecimal color code.`")
        elif code == "WRONG_RGB":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(f":warning:`間違ったRGBカラーコードです.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(f":warning:`Wrong RGB color code.`")
        elif code == "WRONG_COLOR_NAME":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(f":warning:`サポートされていないカラーネームです.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(f":warning:`Not supported color name.`")
        elif code == "UNKNOWN_COLOR_TYPE":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(":warning:`間違ったカラータイプです.hexで16進数, rgbでRGB, nameで色名で指定できます.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(":warning:`Wrong color type. hex is hexadecimal, rgb is RGB, name is a color name.`")
        elif code == "WRONG_COMMAND":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(":warning:`コマンドが間違っています.構文が正しいことを確認してください!`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(":warning:`Wrong command.Please check your arguments are valid!`")
        elif code == "UNKNOWN_ERROR":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(":warning:`不明なエラーが発生しました.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(":warning:`Unknown error has occurred.`")
        elif code == "HELP":
            if lang == LanguageCode.JAPANESE:
                embed = discord.Embed(title="使い方", color=0xffff99, url=self.info["WEB_COMMAND_URL_JA"])
                embed.add_field(name="公式サイトで詳しいコマンドの説明を確認してください!",
                                value="[{0}]({0})".format(self.info["WEB_COMMAND_URL_JA"]), inline=False)
                embed.add_field(name="各種類のコマンドの一覧を表示するには:",
                                value="```yaml\n{0}help music ... 音楽コマンド一覧\n{0}help game ... ゲームコマンド一覧\n{0}help other ... その他のコマンド一覧\n```".format(
                                    self.bot.PREFIX), inline=False)
                embed.add_field(name="さらにmuffinについて知るには:",
                                value="```fix\n{0}invite ... BOTの招待URLを送信します.\n{0}info ... BOTの情報を表示します.\n```".format(
                                    self.bot.PREFIX), inline=False)
                embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿",
                                value="作成者: {} | [公式鯖リンク]({}) | [公式ウェブサイト]({})".format(self.info["AUTHOR"],
                                                                                       self.info["SERVER_URL"],
                                                                                       self.info["WEB_URL_JA"]))
            elif lang == LanguageCode.ENGLISH:
                embed = discord.Embed(title="Usage", color=0xffff99, url=self.info["WEB_COMMAND_URL"])
                embed.add_field(name="Please check commands details on Official WebSite!",
                                value="[{0}]({0})".format(self.info["WEB_COMMAND_URL"]), inline=False)
                embed.add_field(name="To see each type of Commands:",
                                value="```yaml\n{0}help music ... MusicCommands\n{0}help game ... GameCommands\n{0}help other ... OtherCommands\n```".format(
                                    self.bot.PREFIX), inline=False)
                embed.add_field(name="Know more about muffin:",
                                value="```fix\n{0}invite ... Send Invitation link.\n{0}info ... Show BOT information.\n```".format(
                                    self.bot.PREFIX), inline=False)
                embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿",
                                value="Author: {} | [OfficialServer]({}) | [OfficialWebSite]({})".format(
                                    self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL_JA"]),
                                inline=False)
            await ctx.send(embed=embed)
        elif code == "HELP_MUSIC":
            if lang == LanguageCode.JAPANESE:
                embed = discord.Embed(title="使い方 - 音楽コマンド", color=0xff99ff, url=self.info["WEB_COMMAND_URL_MUSIC_JA"])
                embed.add_field(name="使い方の例などは公式サイトで確認できます!",
                                value="[{0}]({0})".format(self.info["WEB_COMMAND_URL_MUSIC_JA"]), inline=False)
                embed.add_field(name="{}join".format(self.info["PREFIX"]), value="BOTをボイスチャンネルに接続します", inline=False)
                embed.add_field(name="{}auto [name]".format(self.info["PREFIX"]), value="指定した曲に関連する曲を連続再生します.",
                                inline=False)
                embed.add_field(name="{}play [name or URL]".format(self.info["PREFIX"]), value="曲名またはURLで音楽を再生します",
                                inline=False)
                embed.add_field(name="{}search [name]".format(self.info["PREFIX"]),
                                value="曲名で曲を検索します.リストが表示された後対応する番号を送信することで再生できます", inline=False)
                embed.add_field(name="{}queue".format(self.info["PREFIX"]), value="予約された曲を表示します", inline=False)
                embed.add_field(name="{}disconnect".format(self.info["PREFIX"]), value="BOTをボイスチャンネルから切断します",
                                inline=False)
                embed.add_field(name="{}loop".format(self.info["PREFIX"]), value="予約されている曲を繰り返します", inline=False)
                embed.add_field(name="{}repeat".format(self.info["PREFIX"]), value="現在再生している曲を繰り返します", inline=False)
                embed.add_field(name="{}pause".format(self.info["PREFIX"]), value="音楽の再生を一時停止します", inline=False)
                embed.add_field(name="{}resume".format(self.info["PREFIX"]), value="音楽の再生を再開します", inline=False)
                embed.add_field(name="{}skip".format(self.info["PREFIX"]), value="現在流している音楽をスキップします", inline=False)
                embed.add_field(name="{}remove [index]".format(self.info["PREFIX"]), value="指定したインデックス番目にある曲を削除します",
                                inline=False)
                embed.add_field(name="{}clear".format(self.info["PREFIX"]), value="予約されている曲を全て削除します", inline=False)
                embed.add_field(name="{}volume [%]".format(self.info["PREFIX"]), value="音量を変更します", inline=False)
                embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿",
                                value="作成者: {} | [公式鯖リンク]({}) | [公式ウェブサイト]({})".format(self.info["AUTHOR"],
                                                                                       self.info["SERVER_URL"],
                                                                                       self.info["WEB_URL_JA"]),
                                inline=False)
            elif lang == LanguageCode.ENGLISH:
                embed = discord.Embed(title="Usage - MusicCommands", color=0xff99ff,
                                      url=self.info["WEB_COMMAND_URL_MUSIC"])
                embed.add_field(name="You can see examples of command on official website!",
                                value="[{0}]({0})".format(self.info["WEB_COMMAND_URL_MUSIC"]), inline=False)
                embed.add_field(name="{}join".format(self.info["PREFIX"]), value="Connect bot to voice channel",
                                inline=False)
                embed.add_field(name="{}auto [name]".format(self.info["PREFIX"]), value="Play related music Continuity",
                                inline=False)
                embed.add_field(name="{}play [name or URL]".format(self.info["PREFIX"]),
                                value="Play music with url or name", inline=False)
                embed.add_field(name="{}search [name]".format(self.info["PREFIX"]),
                                value="Search music with name. Then list of songs will appear so please send number.",
                                inline=False)
                embed.add_field(name="{}queue".format(self.info["PREFIX"]), value="Show queue of server", inline=False)
                embed.add_field(name="{}disconnect".format(self.info["PREFIX"]),
                                value="Disconnect bot from voice channel", inline=False)
                embed.add_field(name="{}loop".format(self.info["PREFIX"]), value="Loop all music in queue",
                                inline=False)
                embed.add_field(name="{}repeat".format(self.info["PREFIX"]),
                                value="Repeat music that is currently playing", inline=False)
                embed.add_field(name="{}pause".format(self.info["PREFIX"]), value="Pause playing music", inline=False)
                embed.add_field(name="{}resume".format(self.info["PREFIX"]), value="Resume playing music", inline=False)
                embed.add_field(name="{}skip".format(self.info["PREFIX"]), value="Skip music currently that is playing",
                                inline=False)
                embed.add_field(name="{}remove [index]".format(self.info["PREFIX"]).format(self.info["PREFIX"]),
                                value="Remove music with index", inline=False)
                embed.add_field(name="{}clear".format(self.info["PREFIX"]), value="Remove all music in queue",
                                inline=False)
                embed.add_field(name="{}volume [%]".format(self.info["PREFIX"]), value="Change volume of music",
                                inline=False)
                embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿",
                                value="Author: {} | [OfficialServer]({}) | [OfficialWebSite]({})".format(
                                    self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL"]), inline=False)
            await ctx.send(embed=embed)
        elif code == "HELP_GAME":
            if lang == LanguageCode.JAPANESE:
                embed = discord.Embed(title="使い方 - ゲームコマンド", color=0xa5642a, url=self.info["WEB_COMMAND_URL_GAME_JA"])
                embed.add_field(name="使い方の例などは公式サイトで確認できます!", value="[{0}]({0})".format(self.info["WEB_COMMAND_URL_GAME_JA"]), inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}rule", value="ShadowChoiceのルールを表示します", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}status [@ユーザー]", value="ステータスを表示します.メンションしなかった場合,自分のステータスが表示されます.", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}shadowchoice [人数] [試合数]", value="試合を開始します.人数,試合数を指定しなかった場合,1人の1戦で開始されます.", inline=False)
                embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="作成者: {} | [公式鯖リンク]({}) | [公式ウェブサイト]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL_JA"]), inline=False)
            elif lang == LanguageCode.ENGLISH:
                embed = discord.Embed(title="Usage - GameCommands", color=0xa5642a, url=self.info["WEB_COMMAND_URL_GAME"])
                embed.add_field(name="You can see examples of command on official website!", value="[{0}]({0})".format(self.info["WEB_COMMAND_URL_GAME"]), inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}rule", value="Show rule of ShadowChoice", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}status [@user]", value="Show status.If you do not mention, your status will be displayed.", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}shadowchoice [player count] [rounds]", value="Start match.If you leave empty, it will starts with singlemode 1round.", inline=False)
                embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="Author: {} | [OfficialServer]({}) | [OfficialWebSite]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL"]), inline=False)
            await ctx.send(embed=embed)
        elif code == "HELP_OTHER":
            if lang == LanguageCode.JAPANESE:
                embed = discord.Embed(title="使い方 - その他のコマンド", color=0x99ffff, url=self.info["WEB_COMMAND_URL_OTHER_JA"])
                embed.add_field(name="使い方の例などは公式サイトで確認できます!", value="[{0}]({0})".format(self.info["WEB_COMMAND_URL_OTHER_JA"]), inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}help", value="このメッセージを表示します", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}info", value="BOTに関する情報を表示します", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}feedback [内容]", value="フィードバックを送信します", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}tr [言語コード] [文章]", value="テキストを翻訳します", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}check [u(ユーザー)/m(メッセージ)/i(招待)] [ID/URL/メンション等]", value="ユーザーIDやメッセージURL,招待URLから詳細情報を取得します.", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}lang", value="言語コード一覧を表示します", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}invite", value="BOTを招待するURLを送信します", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}ping", value="BOTの反応速度を計測します", inline=False)
                embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="作成者: {} | [公式鯖リンク]({}) | [公式ウェブサイト]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL_JA"]), inline=False)
            elif lang == LanguageCode.ENGLISH:
                embed = discord.Embed(title="Usage - OtherCommands", color=0x99ffff, url=self.info["WEB_COMMAND_URL_OTHER"])
                embed.add_field(name="You can see examples of command on official website!", value="[{0}]({0})".format(self.info["WEB_COMMAND_URL_OTHER"]), inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}help", value="Send this message", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}info", value="Show informations about this bot", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}feedback [text]", value="Send feedback.", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}tr [lang] [text]", value="Translate text", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}check [u (user)/m (message)/i (invitation)] [ID/URL/mention etc.]", value="Get detailed information from UserID,MessageURL,InvitationURL etc.", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}lang", value="Show list of language codes", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}invite", value="Send invitation url", inline=False)
                embed.add_field(name=f"{self.bot.PREFIX}ping", value="Show ping of this bot", inline=False)
                embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="Author: {} | [OfficialServer]({}) | [OfficialWebSite]({})".format( self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL"]), inline=False)
            await ctx.send(embed=embed)
        elif code == "INVITE":
            if lang == LanguageCode.JAPANESE:
                embed = discord.Embed(title="招待", url=self.info["INVITE_URL"], color=0x86f9c5)
                embed.set_thumbnail(url=self.bot.user.avatar_url)
                embed.add_field(name="各種招待URL:", value="[BOTの招待URL]({})\n[公式サーバー]({})\n[公式サイト]({})".format(self.info["INVITE_URL"], self.info["SERVER_URL"], self.info["WEB_URL_JA"]), inline=False)
                embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="作成者: {} | [公式鯖リンク]({}) | [公式ウェブサイト]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL"]), inline=False)
            else:
                embed = discord.Embed(title="Invitation", url=self.info["INVITE_URL"], color=0x86f9c5)
                embed.set_thumbnail(url=self.bot.user.avatar_url)
                embed.add_field(name="InviteURLs:", value="[BOTInviteURL]({})\n[SupportServer]({})\n[OfficialWebSite]({})".format(self.info["INVITE_URL"], self.info["SERVER_URL"], self.info["WEB_URL_JA"]), inline=False)
                embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="Author: {} | [OfficialServer]({}) | [OfficialWebSite]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL"]), inline=False)
            await ctx.send(embed=embed)
        elif code == "TRANSLATE_RESULT":
            if lang == LanguageCode.JAPANESE:
                embed = discord.Embed(description=f"```CSS\n[{arg1}]``` ```fix\n{arg2}```", color=0xb6ff01, timestamp=ctx.message.created_at)
            elif lang == LanguageCode.ENGLISH:
                embed = discord.Embed(description=f"```CSS\n[{arg1}]``` ```fix\n{arg2}```", color=0xb6ff01, timestamp=ctx.message.created_at)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
            embed.set_footer(text=f"{ctx.guild.name} | {ctx.channel.name}")
            await ctx.send(embed=embed)
        elif code == "TRANSLATABLE_LANGUAGES":
            if lang == LanguageCode.JAPANESE:
                embed = discord.Embed(title="言語コード一覧", color=0xbc8f8f, description="```CSS\n[アフリカーンス語] ... af\n[アルバニア語] ... sq\n[アムハラ語] ... am\n[アラビア文字] ... ar\n[アルメニア語] ... hy\n[アゼルバイジャン語] ... az\n[バスク語] ... eu\n[ベラルーシ語] ... be\n[ベンガル文字] ... bn\n[ボスニア語] ... bs\n[ブルガリア語] ... bg\n[カタロニア語] ... ca\n[セブ語] ... ceb\n[中国語(簡体)] ... zh-CN または zh\n[中国語(繁体)] ... zh-TW\n[コルシカ語] ... co\n[クロアチア語] ... hr\n[チェコ語] ... cs\n[デンマーク語] ... da\n[オランダ語] ... nl\n[英語] ... en\n[エスペラント語] ... eo\n[エストニア語] ... et\n[フィンランド語] ... fi\n[フランス語] ... fr\n[フリジア語] ... fy\n[ガリシア語] ... gl\n[グルジア語] ... ka\n[ドイツ語] ... de\n[ギリシャ語] ... el\n[グジャラト語] ... gu\n[クレオール語(ハイチ)] ... ht\n[ハウサ語] ... ha\n[ハワイ語] ... haw\n[ヘブライ語] ... he または iw\n[ヒンディー語] ... hi\n[モン語] ... hmn\n[ハンガリー語] ... hu\n[アイスランド語] ... is\n[イボ語] ... ig\n[インドネシア語] ... id\n[アイルランド語] ... ga\n[イタリア語] ... it\n[日本語] ... ja\n[ジャワ語] ... jv\n[カンナダ語] ... kn\n[カザフ語] ... kk\n[クメール語] ... km\n[キニヤルワンダ語] ... rw\n[韓国語] ... ko\n[クルド語] ... ku\n[キルギス語] ... ky\n[ラオ語] ... lo\n[ラテン語] ... la\n[ラトビア語] ... lv\n[リトアニア語] ... lt\n[ルクセンブルク語] ... lb\n[マケドニア語] ... mk\n[マラガシ語] ... mg\n[マレー語] ... ms\n[マラヤーラム文字] ... ml\n[マルタ語] ... mt\n[マオリ語] ... mi\n[マラーティー語] ... mr\n[モンゴル語] ... mn\n[ミャンマー語(ビルマ語)] ... my\n[ネパール語] ... ne\n[ノルウェー語] ... no\n[ニャンジャ語(チェワ語)] ... ny\n[オリヤ語] ... or\n[パシュト語] ... ps\n[ペルシャ語] ... fa\n[ポーランド語] ... pl\n[ポルトガル語(ポルトガル、ブラジル)] ... pt\n[パンジャブ語] ... pa\n[ルーマニア語] ... ro\n[ロシア語] ... ru\n[サモア語] ... sm\n[スコットランド ゲール語] ... gd\n[セルビア語] ... sr\n[セソト語] ... st\n[ショナ語] ... sn\n[シンド語] ... sd\n[シンハラ語] ... si\n[スロバキア語] ... sk\n[スロベニア語] ... sl\n[ソマリ語] ... so\n[スペイン語] ... es\n[スンダ語] ... su\n[スワヒリ語] ... sw\n[スウェーデン語] ... sv\n[タガログ語(フィリピン語)] ... tl\n[タジク語] ... tg\n[タミル語] ... ta\n[タタール語] ... tt\n[テルグ語] ... te\n[タイ語] ... th\n[トルコ語] ... tr\n[トルクメン語] ... tk\n[ウクライナ語] ... uk\n[ウルドゥー語] ... ur\n[ウイグル語] ... ug\n[ウズベク語] ... uz\n[ベトナム語] ... vi\n[ウェールズ語] ... cy\n[コーサ語] ... xh\n[イディッシュ語] ... yi\n[ヨルバ語] ... yo\n[ズールー語] ... zu```")
            elif lang == LanguageCode.ENGLISH:
                embed = discord.Embed(title="Language codes", color=0xbc8f8f, description="```CSS\n[Afrikaans] ... af\n[Albanian] ... sq\n[Amharic] ... am\n[Arabic] ... ar\n[Armenian] ... hy\n[Azerbaijani] ... az\n[Basque] ... eu\n[Belarusian] ... be\n[Bengali] ... bn\n[Bosnian] ... bs\n[Bulgarian] ... bg\n[Catalan] ... ca\n[Cebuano] ... ceb \n[Chinese (Simplified)] ... zh-CN or zh \n[Chinese (Traditional)] ... zh-TW \n[Corsican] ... co\n[Croatian] ... hr\n[Czech] ... cs\n[Danish] ... da\n[Dutch] ... nl\n[English] ... en\n[Esperanto] ... eo\n[Estonian] ... et\n[Finnish] ... fi\n[French] ... fr\n[Frisian] ... fy\n[Galician] ... gl\n[Georgian] ... ka\n[German] ... de\n[Greek] ... el\n[Gujarati] ... gu\n[Haitian Creole] ... ht\n[Hausa] ... ha\n[Hawaiian] ... haw \n[Hebrew] ... he or iw\n[Hindi] ... hi\n[Hmong] ... hmn \n[Hungarian] ... hu\n[Icelandic] ... is\n[Igbo] ... ig\n[Indonesian] ... id\n[Irish] ... ga\n[Italian] ... it\n[Japanese] ... ja\n[Javanese] ... jv\n[Kannada] ... kn\n[Kazakh] ... kk\n[Khmer] ... km\n[Kinyarwanda] ... rw\n[Korean] ... ko\n[Kurdish] ... ku\n[Kyrgyz] ... ky\n[Lao] ... lo\n[Latin] ... la\n[Latvian] ... lv\n[Lithuanian] ... lt\n[Luxembourgish] ... lb\n[Macedonian] ... mk\n[Malagasy] ... mg\n[Malay] ... ms\n[Malayalam] ... ml\n[Maltese] ... mt\n[Maori] ... mi\n[Marathi] ... mr\n[Mongolian] ... mn\n[Myanmar (Burmese)] ... my\n[Nepali] ... ne\n[Norwegian] ... no\n[Nyanja (Chichewa)] ... ny\n[Odia (Oriya)] ... or\n[Pashto] ... ps\n[Persian] ... fa\n[Polish] ... pl\n[Portuguese (Portugal, Brazil)] ... pt\n[Punjabi] ... pa\n[Romanian] ... ro\n[Russian] ... ru\n[Samoan] ... sm\n[Scots Gaelic] ... gd\n[Serbian] ... sr\n[Sesotho] ... st\n[Shona] ... sn\n[Sindhi] ... sd\n[Sinhala (Sinhalese)] ... si\n[Slovak] ... sk\n[Slovenian] ... sl\n[Somali] ... so\n[Spanish] ... es\n[Sundanese] ... su\n[Swahili] ... sw\n[Swedish] ... sv\n[Tagalog (Filipino)] ... tl\n[Tajik] ... tg\n[Tamil] ... ta\n[Tatar] ... tt\n[Telugu] ... te\n[Thai] ... th\n[Turkish] ... tr\n[Turkmen] ... tk\n[Ukrainian] ... uk\n[Urdu] ... ur\n[Uyghur] ... ug\n[Uzbek] ... uz\n[Vietnamese] ... vi\n[Welsh] ... cy\n[Xhosa] ... xh\n[Yiddish] ... yi\n[Yoruba] ... yo\n[Zulu] ... zu```")
            await ctx.send(embed=embed)

    async def report_error(self, ctx, name, message):
        """
        エラーをログチャンネルに送信
        :param ctx: Context
        :param name: 関数名
        :param message: エラーメッセージ
        :return:
        """
        channel = self.bot.get_channel(self.info["ERROR_CHANNEL"])
        try:
            embed = discord.Embed(title=name, description=message)
            embed.set_author(name="Error Reporter")
            await channel.send(embed=embed)
        except:
            embed = discord.Embed(title=name, description="<TOO LONG>")
            embed.set_author(name="Error Reporter")
            msg = await channel.send(embed=embed, file=discord.File(fp=io.StringIO(message), filename="error.txt"))

    async def show_user_info(self, ctx, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
        except discord.errors.NotFound:
            return await self.send_text(ctx, "INVALID_ID", user_id)
        lang = get_language(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        embed = discord.Embed(title=str(user), color=0x66cdaa)
        embed.add_field(name="ID", value=user.id)
        embed.set_thumbnail(url=user.avatar_url)
        if lang == LanguageCode.JAPANESE:
            embed.add_field(name="アカウント作成日", value=user.created_at.strftime("%Y/%m/%d %H:%M:%S"))
        elif lang == LanguageCode.ENGLISH:
            embed.add_field(name="AccountCreated", value=user.created_at.strftime("%Y/%m/%d %H:%M:%S"))
        member = ctx.guild.get_member(user_id)
        if member is not None:
            status = ""
            if str(member.mobile_status) != "offline":
                status += f"Mobile: {member.mobile_status},"
            if str(member.desktop_status) != "offline":
                status += f"Desktop: {member.desktop_status},"
            if str(member.web_status) != "offline":
                status += f"Web: {member.web_status}"
            status = status.replace(",", "\n")
            if status == "":
                status = "offline"
            if lang == LanguageCode.JAPANESE:
                embed.add_field(name="サーバー参加日", value=member.joined_at.strftime("%Y/%m/%d %H:%M:%S"), inline=False)
                embed.add_field(name="ニックネーム", value=member.display_name)
                embed.add_field(name="ステータス", value=status)
            elif lang == LanguageCode.ENGLISH:
                embed.add_field(name="UserJoined", value=member.joined_at.strftime("%Y/%m/%d %H:%M:%S"), inline=False)
                embed.add_field(name="NickName", value=member.display_name)
                embed.add_field(name="Status", value=status)
        await ctx.send(embed=embed)

    async def show_invite_info(self, ctx, invite_code):
        try:
            invite = await self.bot.fetch_invite(url=invite_code)
        except discord.errors.NotFound:
            return await self.send_text(ctx, "INVALID_LINK", invite_code)
        lang = get_language(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        embed = discord.Embed(title=invite_code, url=invite.url, color=0x98fb98)
        embed.set_author(name=invite.guild.name, icon_url=invite.guild.icon_url)
        embed.set_thumbnail(url=invite.guild.icon_url)
        if lang == LanguageCode.JAPANESE:
            embed.add_field(name="サーバー名", value=invite.guild.name, inline=False)
            embed.add_field(name="サーバーID", value=invite.guild.id)
            embed.add_field(name="招待者", value=str(invite.inviter), inline=False)
            embed.add_field(name="招待先チャンネル", value=invite.channel.name)
            embed.add_field(name="アクティブメンバー人数", value=invite.approximate_presence_count, inline=False)
            embed.add_field(name="メンバー人数", value=invite.approximate_member_count)
            embed.set_footer(text="この招待リンクは有効です.")
        elif lang == LanguageCode.ENGLISH:
            embed.add_field(name="ServerName", value=invite.guild.name, inline=False)
            embed.add_field(name="ServerID", value=invite.guild.id)
            embed.add_field(name="Inviter", value=str(invite.inviter), inline=False)
            embed.add_field(name="Channel", value=invite.channel.name)
            embed.add_field(name="ActiveMemberCount", value=invite.approximate_presence_count, inline=False)
            embed.add_field(name="MemberCount", value=invite.approximate_member_count)
            embed.set_footer(text="This URL available.")
        await ctx.send(embed=embed)

    @commands.group(aliases=["h"])
    async def help(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.send_text(ctx, "HELP")

    @help.command(name="music", aliases=["Music", "m", "M"])
    async def help_music(self, ctx):
        await self.send_text(ctx, "HELP_MUSIC")

    @help.command(name="game", aliases=["Game", "g", "G"])
    async def help_game(self, ctx):
        await self.send_text(ctx, "HELP_GAME")

    @help.command(name="other", aliases=["Other", "o", "O"])
    async def help_other(self, ctx):
        await self.send_text(ctx, "HELP_OTHER")

    @commands.command(aliases=['inv'])
    async def invite(self, ctx):
        await self.send_text(ctx, "INVITE")

    @commands.command(aliases=['i'])
    async def info(self, ctx):
        guilds = len(self.bot.guilds)
        users = len(self.bot.users)
        text_channels = 0
        voice_channels = 0
        for channel in self.bot.get_all_channels():
            if isinstance(channel, discord.TextChannel):
                text_channels += 1
            elif isinstance(channel, discord.VoiceChannel):
                voice_channels += 1
        td = datetime.timedelta(seconds=int(time.time() - self.bot.uptime))
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        d = td.days
        embed: discord.Embed
        lang = get_language(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        if lang == LanguageCode.JAPANESE:
            embed = discord.Embed(title="情報", color=0x86f9c5, url=self.info["WEB_URL_JA"])
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.add_field(name="管理者:", value=self.info["AUTHOR"], inline=False)
            embed.add_field(name="ステータス", value=f"```サーバー数:{guilds}\nテキストチャンネル数:{text_channels}\nボイスチャンネル:{voice_channels}\nユーザー数:{users}```", inline=False)
            embed.add_field(name="稼働時間", value=f"{d}日 {h}時間 {m}分 {s}秒", inline=False)
            embed.add_field(name="URL:", value="[BOTの招待]({}) | [公式鯖]({}) | [公式ウェブサイト]({}) | [寄付]({})".format(self.info["INVITE_URL"], self.info["SERVER_URL"], self.info["WEB_URL_JA"], self.info["WEB_DONATE_URL_JA"]))
        elif lang == LanguageCode.ENGLISH:
            embed = discord.Embed(title="Information", color=0x86f9c5, url=self.info["WEB_URL"])
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.add_field(name="Creator:", value=self.info["AUTHOR"], inline=False)
            embed.add_field(name="Status", value=f"```Servers:{guilds}\nTextChannels:{text_channels}\nVoiceChannels:{voice_channels}\nUsers:{users}```", inline=False)
            embed.add_field(name="Uptime", value=f"{d}d {h}h {m}m {s}s", inline=False)
            embed.add_field(name="URL:", value="[invitation]({}) | [OfficialServer]({}) | [OfficialWebSite]({}) | [Donate]({})".format(self.info["INVITE_URL"], self.info["SERVER_URL"], self.info["WEB_URL"], self.info["WEB_DONATE_URL"]))
        await ctx.send(embed=embed)

    @commands.command(aliases=['tr'])
    async def trans(self, ctx, lang, *, text):
        try:
            lang_list = ["af", "sq", "am", "ar", "hy", "az", "eu", "be", "bn", "bs", "bg", "ca", "ceb", "zh-CN", "zh", "zh-TW", "co", "hr", "cs", "da", "nl", "en", "eo", "et", "fi", "fr", "fy", "gl", "ka", "de", "el", "gu", "ht", "ha", "haw", "he iw", "hi", "hmn", "hu", "is", "ig", "id", "ga", "it", "ja", "jv", "kn", "kk", "km", "rw", "ko", "ku", "ky", "lo", "la", "lv", "lt", "lb", "mk", "mg",
                         "ms", "ml", "mt", "mi", "mr", "mn", "my", "ne", "no", "ny", "or", "ps", "fa", "pl", "pt", "pa", "ro", "ru", "sm", "gd", "sr", "st", "sn", "sd", "si", "sk", "sl", "so", "es", "su", "sw", "sv", "tl", "tg", "ta", "tt", "te", "th", "tr", "tk", "uk", "ur", "ug", "uz", "vi", "cy", "xh", "yi", "yo", "zu"]
            if lang not in lang_list:
                return await self.send_text(ctx, "WRONG_LANG_CODE")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://script.google.com/macros/s/AKfycbzy2M6VEqREaXdAY0Xa_WayFX3B3HhOGVZN8FzT1lPhiHE9_Wk/exec?text={urllib.parse.quote(text)}&target={lang}") as r:
                    if r.status == 200:
                        try:
                            res = await r.json()
                            if len(res["text"]) >= 2048:
                                return await self.send_text(ctx, "TRANS_OVER_2000")
                            await self.send_text(ctx, "TRANSLATE_RESULT", arg1=lang, arg2=res["text"])
                        except:
                            await self.send_text(ctx, "INVALID_STRING")
                            await self.report_error(ctx, name="trans", message=pprint.pformat(r))
                    elif r.status == 400:
                        await self.send_text(ctx, "INVALID_STRING")
        except:
            await ctx.send(traceback2.format_exc())

    @commands.command(aliases=['tr_lg'])
    async def trans_lang(self, ctx):
        await self.send_text(ctx, "TRANSLATABLE_LANGUAGES")

    @commands.command(aliases=['pg'])
    async def ping(self, ctx):
        before = time.monotonic()
        message = await ctx.send("Pong")
        ping = (time.monotonic() - before) * 1000
        await message.delete()
        await ctx.send(f":white_check_mark:`ping: {int(ping)}[ms]`")

    @commands.command(aliases=["f", "fb"])
    async def feedback(self, ctx, *, text):
        lang = get_language(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        channel = self.bot.get_channel(self.info["ERROR_CHANNEL"])
        embed = discord.Embed(title="お問い合わせ", description="サーバー:{0.name}({0.id})\nチャンネル:{1.name}({1.id})\nユーザー:{2}({2.id})".format(ctx.guild, ctx.channel, ctx.author))
        embed.add_field(name="内容:", value=text, inline=False)
        embed.add_field(name="お問い合わせID:", value=ctx.message.id)
        embed.set_footer(text=datetime.datetime.now().strftime('%Y年%m月%d日 %H時%M分'))
        msg = await channel.send(embed=embed)
        if lang == LanguageCode.JAPANESE:
            await ctx.send(f":white_check_mark:お問い合わせが完了しました.\n内容によってはBOT管理者がお返事を公式サーバーにて掲示いたします.\n貴重なご意見ありがとうございました。\nお問い合わせID: {ctx.message.id}")
        elif lang == LanguageCode.ENGLISH:
            await ctx.send(f":white_check_mark: Your inquiry is complete.\nDepending on the content, the BOT administrator will post a reply on the official server.\nThank you for your valuable feedback.\nFeedback ID: {ctx.message.id}")

    @commands.group(aliases=["chk"])
    async def check(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("check <user|invite|message> <ID|URL>")

    @check.command(name="user", aliases=["u"])
    async def check_user(self, ctx):
        user_list = []
        if ctx.message.mentions != []:
            for target in ctx.message.mentions:
                user_list.append(target.id)
        else:
            text = ctx.message.content.split(" ")
            if len(text) >= 3:
                for user_id in text[2:]:
                    result = re.search(self.user_match, user_id)
                    if result is not None:
                        user_list.append(int(result["userid"]))
                    else:
                        await self.send_text(ctx, "INVALID_ID", user_id)
            else:
                return await self.send(ctx, "PLS_SPECIFY_WITH_ID_OR_MENTION")

        for user_id in user_list:
            await self.show_user_info(ctx, user_id)

    @check.command(name="invite", aliases=["i", "inv"])
    async def check_invite(self, ctx, *, text):
        invite_list = []
        invites = text.split()
        for invite in invites:
            result = re.search(self.invite_match, invite)
            if result is not None:
                invite_list.append(result["invitecode"])
            else:
                result2 = re.search(self.invite_match2, invite)
                if result2 is not None:
                    invite_list.append(result2["invitecode"])
                else:
                    await self.send_text(ctx, "INVALID_LINK", invite)

        for invite in invite_list:
            await self.show_invite_info(ctx, invite)

    @check.command(name="message", aliases=["m", "msg"])
    async def check_message(self, ctx, *, text):
        msg_list = []
        messages = text.split()
        for message in messages:
            result = re.search(self.message_match, message)
            if result is not None:
                msg_list.append({"message": int(result["message"]), "channel": int(result["channel"]), "guild": int(result["guild"])})
            else:
                await self.send_text(ctx, "INVALID_MESSAGE", message)

        for message in msg_list:
            if message["guild"] != ctx.guild.id:
                await self.send_text(ctx, "CANNOT_GET_CUZ_ANOTHER_SERVER")
            else:
                channel = ctx.guild.get_channel(message["channel"])
                msg = await channel.fetch_message(message["message"])
                embed = discord.Embed(timestamp=msg.created_at, description=msg.content, color=0xfa8072)
                embed.set_author(name=str(msg.author), icon_url=msg.author.avatar_url)
                embed.set_footer(text=f"{msg.guild.name} | {msg.channel.name}")
                if msg.attachments and msg.attachments[0].proxy_url:
                    embed.set_image(url=msg.attachments[0].proxy_url)
                await ctx.send(embed=embed)

    @commands.group(aliases=["clr"])
    async def color(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.send_text(ctx, "UNKNOWN_COLOR_TYPE")

    @color.command(name="hex", aliases=["h"])
    async def color_hex_command(self, ctx, text):
        result = re.search(self.color_match, text)
        if result is None:
            return await self.send_text(ctx, "WRONG_HEX_CODE")
        hex_color = result["color"]
        rgb = self.hex_to_rgb(hex_color)
        try:
            color_name = webcolors.hex_to_name(f"#{hex_color}")
        except:
            color_name = "???"
        embed = discord.Embed(title=f"Hex: {hex_color}", color=int(f'0x{hex_color}', 16))
        embed.add_field(name="hex", value=f"#{hex_color}", inline=False)
        embed.add_field(name="rgb", value=f"r: {rgb[0]}, g:{rgb[1]}, b:{rgb[2]}", inline=False)
        embed.add_field(name="name", value=color_name)
        await ctx.send(embed=embed)

    @color.command(name="rgb", aliases=["r"])
    async def color_rgb_command(self, ctx, r, g, b):
        if not (r.isdigit() and g.isdigit() and b.isdigit()):
            return await self.send_text(ctx, "WRONG_RGB")
        elif not (int(r) <= 255 and int(g) <= 255 and int(b) <= 255):
            return await self.send_text(ctx, "WRONG_RGB")
        r = int(r);
        g = int(g);
        b = int(b)
        hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
        try:
            color_name = webcolors.hex_to_name(hex_color)
        except:
            color_name = "???"
        embed = discord.Embed(title=f"RGB: {r} {g} {b}", color=int(f'0x{hex_color.replace("#", "")}', 16))
        embed.add_field(name="hex", value=hex_color, inline=False)
        embed.add_field(name="rgb", value=f"r: {r}, g:{g}, b:{b}", inline=False)
        embed.add_field(name="name", value=color_name)
        await ctx.send(embed=embed)

    @color.command(name="name", aliases=["n"])
    async def color_name_command(self, ctx, text):
        try:
            hex_color = webcolors.CSS3_NAMES_TO_HEX[text.lower()]
        except:
            return await self.send_text(ctx, "WRONG_COLOR_NAME")
        rgb = self.hex_to_rgb(hex_color.replace("#", ""))
        embed = discord.Embed(title=f"Name: {text.lower()}", color=int(f'0x{hex_color.replace("#", "")}', 16))
        embed.add_field(name="hex", value=hex_color, inline=False)
        embed.add_field(name="rgb", value=f"r: {rgb[0]}, g:{rgb[1]}, b:{rgb[2]}", inline=False)
        embed.add_field(name="name", value=text.lower())
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Other(bot))
