# import
from discord.ext import commands
import aiohttp, asyncio, datetime, discord, json, os, pprint, sys, time, urllib, traceback2


class Other(commands.Cog):

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        with open("./INFO.json") as F:
            info = json.load(F)
        self.info = info
        self.load_roles()

    def load_roles(self):
        with open("./ROLE.json") as F:
            roles = json.load(F)
        self.ADMIN = roles["ADMIN"]
        self.Contributor = roles["Contributor"]
        self.BAN = roles["BAN"]

    async def cog_before_invoke(self, ctx):
        self.load_roles()
        if ctx.author.id in self.BAN:
            if str(ctx.guild.region) == "japan":
                await ctx.send(":warning:`あなたはBANされているため,使用できません.\n異議申し立ては公式サーバーにてお願いします.`")
                raise commands.CommandError("Your Account Banned")
            else:
                await ctx.send(":warning:`You cannnot use because you are banned.\nFor objection please use Official Server.`")
                raise commands.CommandError("Your Account Banned")

    @commands.command(aliases=["h"])
    async def help(self, ctx):
        try:
            cmd = ctx.message.content.split()
            if len(cmd) == 1:
                if str(ctx.guild.region) == "japan":
                    embed = discord.Embed(title="使い方", color=0xffff99, url=self.info["WEB_COMMAND_URL_JA"])
                    embed.add_field(name="公式サイトで詳しいコマンドの説明を確認してください!", value="[{0}]({0})".format(self.info["WEB_COMMAND_URL_JA"]), inline=False)
                    embed.add_field(name="各種類のコマンドの一覧を表示するには:", value="```yaml\n{0}help music ... 音楽コマンド一覧\n{0}help game ... ゲームコマンド一覧\n{0}help other ... その他のコマンド一覧\n```".format(self.info["PREFIX"]), inline=False)
                    embed.add_field(name="さらにmuffinについて知るには:", value="```fix\n{0}invite ... BOTの招待URLを送信します.\n{0}info ... BOTの情報を表示します.\n```".format(self.info["PREFIX"]), inline=False)
                    embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="作成者: {} | [公式鯖リンク]({}) | [公式ウェブサイト]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL_JA"]))
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="Usage", color=0xffff99, url=self.info["WEB_COMMAND_URL"])
                    embed.add_field(name="Please check commands details on Official WebSite!", value="[{0}]({0})".format(self.info["WEB_COMMAND_URL"]), inline=False)
                    embed.add_field(name="To see each type of Commands:", value="```yaml\n{0}help music ... MusicCommands\n{0}help game ... GameCommands\n{0}help other ... OtherCommands\n```".format(self.info["PREFIX"]), inline=False)
                    embed.add_field(name="Know more about muffin:", value="```fix\n{0}invite ... Send Invitation link.\n{0}info ... Show BOT information.\n```".format(self.info["PREFIX"]), inline=False)
                    embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="Author: {} | [OfficialServer]({}) | [OfficialWebSite]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL_JA"]), inline=False)
                    await ctx.send(embed=embed)
            elif len(cmd) == 2:
                if cmd[1].startswith("m") or cmd[1].startswith("M"):
                    if str(ctx.guild.region) == "japan":
                        embed=discord.Embed(title="使い方 - 音楽コマンド", color=0xff99ff, url=self.info["WEB_COMMAND_URL_MUSIC_JA"])
                        embed.add_field(name="使い方の例などは公式サイトで確認できます!", value="[{0}]({0})".format(self.info["WEB_COMMAND_URL_MUSIC_JA"]), inline=False)
                        embed.add_field(name="{}join".format(self.info["PREFIX"]), value="BOTをボイスチャンネルに接続します", inline=False)
                        embed.add_field(name="{}auto [name]".format(self.info["PREFIX"]), value="指定した曲に関連する曲を連続再生します.", inline=False)
                        embed.add_field(name="{}play [name or URL]".format(self.info["PREFIX"]), value="曲名またはURLで音楽を再生します", inline=False)
                        embed.add_field(name="{}search [name]".format(self.info["PREFIX"]), value="曲名で曲を検索します.リストが表示された後対応する番号を送信することで再生できます", inline=False)
                        embed.add_field(name="{}queue".format(self.info["PREFIX"]), value="予約された曲を表示します", inline=False)
                        embed.add_field(name="{}disconnect".format(self.info["PREFIX"]), value="BOTをボイスチャンネルから切断します", inline=False)
                        embed.add_field(name="{}loop".format(self.info["PREFIX"]), value="予約されている曲を繰り返します", inline=False)
                        embed.add_field(name="{}repeat".format(self.info["PREFIX"]), value="現在再生している曲を繰り返します", inline=False)
                        embed.add_field(name="{}pause".format(self.info["PREFIX"]), value="音楽の再生を一時停止します", inline=False)
                        embed.add_field(name="{}resume".format(self.info["PREFIX"]), value="音楽の再生を再開します", inline=False)
                        embed.add_field(name="{}skip".format(self.info["PREFIX"]), value="現在流している音楽をスキップします", inline=False)
                        embed.add_field(name="{}remove [index]".format(self.info["PREFIX"]), value="指定したインデックス番目にある曲を削除します", inline=False)
                        embed.add_field(name="{}clear".format(self.info["PREFIX"]), value="予約されている曲を全て削除します", inline=False)
                        embed.add_field(name="{}volume [%]".format(self.info["PREFIX"]), value="音量を変更します", inline=False)
                        embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="作成者: {} | [公式鯖リンク]({}) | [公式ウェブサイト]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL_JA"]), inline=False)
                    else:
                        embed=discord.Embed(title="Usage - MusicCommands", color=0xff99ff, url=self.info["WEB_COMMAND_URL_MUSIC"])
                        embed.add_field(name="You can see examples of command on official website!", value="[{0}]({0})".format(self.info["WEB_COMMAND_URL_MUSIC"]), inline=False)
                        embed.add_field(name="{}join".format(self.info["PREFIX"]), value="Connect bot to voice channel", inline=False)
                        embed.add_field(name="{}auto [name]".format(self.info["PREFIX"]), value="Play related music Continuity", inline=False)
                        embed.add_field(name="{}play [name or URL]".format(self.info["PREFIX"]), value="Play music with url or name", inline=False)
                        embed.add_field(name="{}search [name]".format(self.info["PREFIX"]), value="Search music with name. Then list of songs will appear so please send number.", inline=False)
                        embed.add_field(name="{}queue".format(self.info["PREFIX"]), value="Show queue of server", inline=False)
                        embed.add_field(name="{}disconnect".format(self.info["PREFIX"]), value="Disconnect bot from voice channel", inline=False)
                        embed.add_field(name="{}loop".format(self.info["PREFIX"]), value="Loop all music in queue", inline=False)
                        embed.add_field(name="{}repeat".format(self.info["PREFIX"]), value="Repeat music that is currently playing", inline=False)
                        embed.add_field(name="{}pause".format(self.info["PREFIX"]), value="Pause playing music", inline=False)
                        embed.add_field(name="{}resume".format(self.info["PREFIX"]), value="Resume playing music", inline=False)
                        embed.add_field(name="{}skip".format(self.info["PREFIX"]), value="Skip music currently that is playing", inline=False)
                        embed.add_field(name="{}remove [index]".format(self.info["PREFIX"]).format(self.info["PREFIX"]), value="Remove music with index", inline=False)
                        embed.add_field(name="{}clear".format(self.info["PREFIX"]), value="Remove all music in queue", inline=False)
                        embed.add_field(name="{}volume [%]".format(self.info["PREFIX"]), value="Change volume of music", inline=False)
                        embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="Author: {} | [OfficialServer]({}) | [OfficialWebSite]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL"]), inline=False)
                    await ctx.send(embed=embed)
                elif cmd[1].startswith("g") or cmd[1].startswith("G"):
                    if str(ctx.guild.region) == "japan":
                        await ctx.send("Game機能は現在β版であり、不安定である可能性があります.\n最新情報は公式サイト、公式サーバーで確認できます.")
                    #     embed=discord.Embed(title="使い方 - ゲームコマンド", color=0x99ffff, url=self.info["WEB_COMMAND_URL_GAME_JA"])
                    #     embed.add_field(name="使い方の例などは公式サイトで確認できます!", value="[{0}]({0})".format(self.info["WEB_COMMAND_URL_GAME_JA"]), inline=False)
                    #     embed.add_field(name="{}rule".format(self.info["PREFIX"]), value="ShadowChoiceのルールを表示します", inline=False)
                    #     embed.add_field(name="{}status [@ユーザー]".format(self.info["PREFIX"]), value="ステータスを表示します.メンションしなかった場合,自分のステータスが表示されます.", inline=False)
                    #     embed.add_field(name="{}shadowchoice [人数] [試合数]".format(self.info["PREFIX"]), value="試合を開始します.人数,試合数を指定しなかった場合,1人の1戦で開始されます.", inline=False)
                    #     embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="作成者: {} | [公式鯖リンク]({}) | [公式ウェブサイト]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL_JA"]), inline=False)
                    else:
                        await ctx.send(
                            "Game is currently in beta version and may be unstable.\nThe latest information can be found on the official website and official server.")
                    #     embed=discord.Embed(title="Usage - GameCommands", color=0x99ffff, url=self.info["WEB_COMMAND_URL_GAME"])
                    #     embed.add_field(name="You can see examples of command on official website!", value="[{0}]({0})".format(self.info["WEB_COMMAND_URL_GAME"]), inline=False)
                    #     embed.add_field(name="{}rule".format(self.info["PREFIX"]), value="Show rule of ShadowChoice", inline=False)
                    #     embed.add_field(name="{}status [@user]".format(self.info["PREFIX"]), value="Show status.If you do not mention, your status will be displayed.", inline=False)
                    #     embed.add_field(name="{}shadowchoice [player count] [rounds]".format(self.info["PREFIX"]), value="Start match.If you leave empty, it will starts with singlemode 1round.", inline=False)
                    #     embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="Author: {} | [OfficialServer]({}) | [OfficialWebSite]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL"]), inline=False)
                    # await ctx.send(embed=embed)
                elif cmd[1].startswith("o") or cmd[1].startswith("O"):
                    if str(ctx.guild.region) == "japan":
                        embed = discord.Embed(title="使い方 - その他のコマンド", color=0x99ffff, url=self.info["WEB_COMMAND_URL_OTHER_JA"])
                        embed.add_field(name="使い方の例などは公式サイトで確認できます!", value="[{0}]({0})".format(self.info["WEB_COMMAND_URL_OTHER_JA"]), inline=False)
                        embed.add_field(name="{}help".format(self.info["PREFIX"]), value="このメッセージを表示します", inline=False)
                        embed.add_field(name="{}info".format(self.info["PREFIX"]), value="BOTに関する情報を表示します", inline=False)
                        embed.add_field(name="{}feedback [内容]".format(self.info["PREFIX"]), value="フィードバックを送信します", inline=False)
                        embed.add_field(name="{}tr [言語コード] [文章]".format(self.info["PREFIX"]), value="テキストを翻訳します", inline=False)
                        embed.add_field(name="{}lang".format(self.info["PREFIX"]), value="言語コード一覧を表示します", inline=False)
                        embed.add_field(name="{}invite".format(self.info["PREFIX"]), value="BOTを招待するURLを送信します", inline=False)
                        embed.add_field(name="{}ping".format(self.info["PREFIX"]), value="BOTの反応速度を計測します", inline=False)
                        embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="作成者: {} | [公式鯖リンク]({}) | [公式ウェブサイト]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL_JA"]), inline=False)
                    else:
                        embed=discord.Embed(title="Usage - OtherCommands", color=0x99ffff, url=self.info["WEB_COMMAND_URL_OTHER"])
                        embed.add_field(name="You can see examples of command on official website!", value="[{0}]({0})".format(self.info["WEB_COMMAND_URL_OTHER"]), inline=False)
                        embed.add_field(name="{}help".format(self.info["PREFIX"]), value="Send this message", inline=False)
                        embed.add_field(name="{}info".format(self.info["PREFIX"]), value="Show informations about this bot", inline=False)
                        embed.add_field(name="{}feedback [text]".format(self.info["PREFIX"]), value="Send feedback.", inline=False)
                        embed.add_field(name="{}tr [lang] [text]".format(self.info["PREFIX"]), value="Translate text", inline=False)
                        embed.add_field(name="{}lang".format(self.info["PREFIX"]), value="Show list of language codes", inline=False)
                        embed.add_field(name="{}invite".format(self.info["PREFIX"]), value="Send invitation url", inline=False)
                        embed.add_field(name="{}ping".format(self.info["PREFIX"]), value="Show ping of this bot", inline=False)
                        embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="Author: {} | [OfficialServer]({}) | [OfficialWebSite]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL"]), inline=False)
                    await ctx.send(embed=embed)
            else:
                if str(ctx.guild.region) == "japan":
                    await ctx.send(":warning:`コマンドが間違っています`")
                else:
                    await ctx.send(":warning:`Wrong command.`")
        except:
            await ctx.send(traceback2.format_exc())

    @commands.command(aliases=['inv'])
    async def invite(self, ctx):
        if str(ctx.guild.region) == "japan":
            embed=discord.Embed(title="招待", url=self.info["INVITE_URL"], color=0x86f9c5)
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.add_field(name="各種招待URL:", value="[BOTの招待URL]({})\n[公式サーバー]({})\n[公式サイト]({})".format(self.info["INVITE_URL"], self.info["SERVER_URL"], self.info["WEB_URL_JA"]), inline=False)
            embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="作成者: {} | [公式鯖リンク]({}) | [公式ウェブサイト]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL"]), inline=False)
        else:
            embed=discord.Embed(title="Invitation", url=self.info["INVITE_URL"], color=0x86f9c5)
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.add_field(name="InviteURLs:", value="[BOTInviteURL]({})\n[SupportServer]({})\n[OfficialWebSite]({})".format(self.info["INVITE_URL"], self.info["SERVER_URL"], self.info["WEB_URL_JA"]), inline=False)
            embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="Author: {} | [OfficialServer]({}) | [OfficialWebSite]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL"]), inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['i'])
    async def info(self, ctx):
        if str(ctx.guild.region) == "japan":
            embed=discord.Embed(title="情報", color=0x86f9c5, url=self.info["WEB_URL_JA"])
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.add_field(name="BOTに関する情報:", value="```fix\nBOTの管理&開発:\n  {}\nPrefix:\n  『 {} 』\n開発言語:\n  Python```".format(self.info["AUTHOR"], self.info["PREFIX"]), inline=False)
            embed.add_field(name="URL:", value="[BOTの招待]({}) | [公式鯖]({}) | [公式ウェブサイト]({})".format(self.info["INVITE_URL"],self.info["SERVER_URL"],self.info["WEB_URL_JA"]))
        else:
            embed=discord.Embed(title="Information", color=0x86f9c5, url=self.info["WEB_URL"])
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.add_field(name="About BOT:", value="```Developer:\n  {}\nPrefix:\n  『 {} 』\nLanguage:\n  Python```".format(self.info["AUTHOR"], self.info["PREFIX"]), inline=False)
            embed.add_field(name="URL:", value="[invitation]({}) | [OfficialServer]({}) | [OfficialWebSite]({})".format(self.info["INVITE_URL"],self.info["SERVER_URL"],self.info["WEB_URL"]))
        await ctx.send(embed=embed)

    @commands.command(aliases=['tr'])
    async def trans(self, ctx, lang, *, text):
        try:
            lang_list = ["af", "sq", "am", "ar", "hy", "az", "eu", "be", "bn", "bs", "bg", "ca", "ceb", "zh-CN", "zh", "zh-TW", "co", "hr", "cs", "da", "nl", "en", "eo", "et", "fi", "fr", "fy", "gl", "ka", "de", "el", "gu", "ht", "ha", "haw", "he iw", "hi", "hmn", "hu", "is", "ig", "id", "ga", "it", "ja", "jv", "kn", "kk", "km", "rw", "ko", "ku", "ky", "lo", "la", "lv", "lt", "lb", "mk", "mg", "ms", "ml", "mt", "mi", "mr", "mn", "my", "ne", "no", "ny", "or", "ps", "fa", "pl", "pt", "pa", "ro", "ru", "sm", "gd", "sr", "st", "sn", "sd", "si", "sk", "sl", "so", "es", "su", "sw", "sv", "tl", "tg", "ta", "tt", "te", "th", "tr", "tk", "uk", "ur", "ug", "uz", "vi", "cy", "xh", "yi", "yo", "zu"]
            if lang not in lang_list:
                if str(ctx.guild.region) == "japan":
                    return await ctx.send(":warning:`言語コードが間違っています. `{}lang` で対応可能な言語コード一覧を確認できます.`".format(self.info["PREFIX"]))
                else:
                    return await ctx.send(":warning:`Wrong lanuage code. Please send `{}lang` to see list of avaiable language codes.`".format(self.info["PREFIX"]))
            async with aiohttp.ClientSession() as session:
                async with session.get("https://script.google.com/macros/s/AKfycbzy2M6VEqREaXdAY0Xa_WayFX3B3HhOGVZN8FzT1lPhiHE9_Wk/exec?text={}&target={}".format(urllib.parse.quote(text), lang)) as r:
                    if r.status == 200:
                        try:
                            res = await r.json()
                            if len(res["text"]) >= 2048:
                                return await ctx.send(":warning:`文字列が2000文字を超えるため翻訳結果を表示できませんでした.`")
                            if str(ctx.guild.region) == "japan":
                                embed = discord.Embed(description="```CSS\n[{}]``` ```fix\n{}```".format(lang, res["text"]), color=0xb6ff01)
                            else:
                                embed = discord.Embed(description="```CSS\n[{}]``` ```fix\n{}```".format(lang, res["text"]), color=0xb6ff01)
                            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                            await ctx.send(embed=embed)
                        except:
                            if str(ctx.guild.region) == "japan":
                                await ctx.send(":warning:`不正な文字列です.`")
                            else:
                                await ctx.send(":warning:`Invalid string.`")
                            await ctx.send(traceback2.format_exc())
                            await self.bot.get_channel(self.info["ERROR_CHANNEL"]).send("trans関数内よりレスポンス:\n```{}```".format(pprint.pformat(r)))
                    elif r.status == 400:
                        if str(ctx.guild.region) == "japan":
                            await ctx.send(":warning:`不正な文字列です.`")
                        else:
                            await ctx.send(":warning:`Invalid string.`")
        except:
            await ctx.send(traceback2.format_exc())

    @commands.command(aliases=['lg'])
    async def lang(self, ctx):
        if str(ctx.guild.region) == "japan":
            embed = discord.Embed(title="言語コード一覧", color=0xbc8f8f ,description="```CSS\n[アフリカーンス語] ... af\n[アルバニア語] ... sq\n[アムハラ語] ... am\n[アラビア文字] ... ar\n[アルメニア語] ... hy\n[アゼルバイジャン語] ... az\n[バスク語] ... eu\n[ベラルーシ語] ... be\n[ベンガル文字] ... bn\n[ボスニア語] ... bs\n[ブルガリア語] ... bg\n[カタロニア語] ... ca\n[セブ語] ... ceb\n[中国語(簡体)] ... zh-CN または zh\n[中国語(繁体)] ... zh-TW\n[コルシカ語] ... co\n[クロアチア語] ... hr\n[チェコ語] ... cs\n[デンマーク語] ... da\n[オランダ語] ... nl\n[英語] ... en\n[エスペラント語] ... eo\n[エストニア語] ... et\n[フィンランド語] ... fi\n[フランス語] ... fr\n[フリジア語] ... fy\n[ガリシア語] ... gl\n[グルジア語] ... ka\n[ドイツ語] ... de\n[ギリシャ語] ... el\n[グジャラト語] ... gu\n[クレオール語(ハイチ)] ... ht\n[ハウサ語] ... ha\n[ハワイ語] ... haw\n[ヘブライ語] ... he または iw\n[ヒンディー語] ... hi\n[モン語] ... hmn\n[ハンガリー語] ... hu\n[アイスランド語] ... is\n[イボ語] ... ig\n[インドネシア語] ... id\n[アイルランド語] ... ga\n[イタリア語] ... it\n[日本語] ... ja\n[ジャワ語] ... jv\n[カンナダ語] ... kn\n[カザフ語] ... kk\n[クメール語] ... km\n[キニヤルワンダ語] ... rw\n[韓国語] ... ko\n[クルド語] ... ku\n[キルギス語] ... ky\n[ラオ語] ... lo\n[ラテン語] ... la\n[ラトビア語] ... lv\n[リトアニア語] ... lt\n[ルクセンブルク語] ... lb\n[マケドニア語] ... mk\n[マラガシ語] ... mg\n[マレー語] ... ms\n[マラヤーラム文字] ... ml\n[マルタ語] ... mt\n[マオリ語] ... mi\n[マラーティー語] ... mr\n[モンゴル語] ... mn\n[ミャンマー語(ビルマ語)] ... my\n[ネパール語] ... ne\n[ノルウェー語] ... no\n[ニャンジャ語(チェワ語)] ... ny\n[オリヤ語] ... or\n[パシュト語] ... ps\n[ペルシャ語] ... fa\n[ポーランド語] ... pl\n[ポルトガル語(ポルトガル、ブラジル)] ... pt\n[パンジャブ語] ... pa\n[ルーマニア語] ... ro\n[ロシア語] ... ru\n[サモア語] ... sm\n[スコットランド ゲール語] ... gd\n[セルビア語] ... sr\n[セソト語] ... st\n[ショナ語] ... sn\n[シンド語] ... sd\n[シンハラ語] ... si\n[スロバキア語] ... sk\n[スロベニア語] ... sl\n[ソマリ語] ... so\n[スペイン語] ... es\n[スンダ語] ... su\n[スワヒリ語] ... sw\n[スウェーデン語] ... sv\n[タガログ語(フィリピン語)] ... tl\n[タジク語] ... tg\n[タミル語] ... ta\n[タタール語] ... tt\n[テルグ語] ... te\n[タイ語] ... th\n[トルコ語] ... tr\n[トルクメン語] ... tk\n[ウクライナ語] ... uk\n[ウルドゥー語] ... ur\n[ウイグル語] ... ug\n[ウズベク語] ... uz\n[ベトナム語] ... vi\n[ウェールズ語] ... cy\n[コーサ語] ... xh\n[イディッシュ語] ... yi\n[ヨルバ語] ... yo\n[ズールー語] ... zu```")
        else:
            embed = discord.Embed(title="Language codes", color=0xbc8f8f ,description="```CSS\n[Afrikaans] ... af\n[Albanian] ... sq\n[Amharic] ... am\n[Arabic] ... ar\n[Armenian] ... hy\n[Azerbaijani] ... az\n[Basque] ... eu\n[Belarusian] ... be\n[Bengali] ... bn\n[Bosnian] ... bs\n[Bulgarian] ... bg\n[Catalan] ... ca\n[Cebuano] ... ceb \n[Chinese (Simplified)] ... zh-CN or zh \n[Chinese (Traditional)] ... zh-TW \n[Corsican] ... co\n[Croatian] ... hr\n[Czech] ... cs\n[Danish] ... da\n[Dutch] ... nl\n[English] ... en\n[Esperanto] ... eo\n[Estonian] ... et\n[Finnish] ... fi\n[French] ... fr\n[Frisian] ... fy\n[Galician] ... gl\n[Georgian] ... ka\n[German] ... de\n[Greek] ... el\n[Gujarati] ... gu\n[Haitian Creole] ... ht\n[Hausa] ... ha\n[Hawaiian] ... haw \n[Hebrew] ... he or iw\n[Hindi] ... hi\n[Hmong] ... hmn \n[Hungarian] ... hu\n[Icelandic] ... is\n[Igbo] ... ig\n[Indonesian] ... id\n[Irish] ... ga\n[Italian] ... it\n[Japanese] ... ja\n[Javanese] ... jv\n[Kannada] ... kn\n[Kazakh] ... kk\n[Khmer] ... km\n[Kinyarwanda] ... rw\n[Korean] ... ko\n[Kurdish] ... ku\n[Kyrgyz] ... ky\n[Lao] ... lo\n[Latin] ... la\n[Latvian] ... lv\n[Lithuanian] ... lt\n[Luxembourgish] ... lb\n[Macedonian] ... mk\n[Malagasy] ... mg\n[Malay] ... ms\n[Malayalam] ... ml\n[Maltese] ... mt\n[Maori] ... mi\n[Marathi] ... mr\n[Mongolian] ... mn\n[Myanmar (Burmese)] ... my\n[Nepali] ... ne\n[Norwegian] ... no\n[Nyanja (Chichewa)] ... ny\n[Odia (Oriya)] ... or\n[Pashto] ... ps\n[Persian] ... fa\n[Polish] ... pl\n[Portuguese (Portugal, Brazil)] ... pt\n[Punjabi] ... pa\n[Romanian] ... ro\n[Russian] ... ru\n[Samoan] ... sm\n[Scots Gaelic] ... gd\n[Serbian] ... sr\n[Sesotho] ... st\n[Shona] ... sn\n[Sindhi] ... sd\n[Sinhala (Sinhalese)] ... si\n[Slovak] ... sk\n[Slovenian] ... sl\n[Somali] ... so\n[Spanish] ... es\n[Sundanese] ... su\n[Swahili] ... sw\n[Swedish] ... sv\n[Tagalog (Filipino)] ... tl\n[Tajik] ... tg\n[Tamil] ... ta\n[Tatar] ... tt\n[Telugu] ... te\n[Thai] ... th\n[Turkish] ... tr\n[Turkmen] ... tk\n[Ukrainian] ... uk\n[Urdu] ... ur\n[Uyghur] ... ug\n[Uzbek] ... uz\n[Vietnamese] ... vi\n[Welsh] ... cy\n[Xhosa] ... xh\n[Yiddish] ... yi\n[Yoruba] ... yo\n[Zulu] ... zu```")
        await ctx.send(embed=embed)

    @commands.command(aliases=['pg'])
    async def ping(self, ctx):
        before = time.monotonic()
        message = await ctx.send("Pong")
        ping = (time.monotonic() - before) * 1000
        await message.delete()
        if str(ctx.guild.region) == "japan":
            embed = discord.Embed(title="Ping", color=0x8eb8ff, url=self.info["WEB_URL_JA"])
            embed.add_field(name="反応速度:", value="{}[ms]".format(int(ping)), inline=False)
            embed.add_field(name="接続数:", value="{}".format(len(self.bot.voice_clients)), inline=False)
            embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="作成者: {} | [公式鯖リンク]({}) | [公式ウェブサイト]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL_JA"]), inline=False)
        else:
            embed = discord.Embed(title="Ping", color=0x8eb8ff, url=self.info["WEB_URL"])
            embed.add_field(name="Speed:", value="{}[ms]".format(int(ping)), inline=False)
            embed.add_field(name="Connecting:", value="{}".format(len(self.bot.voice_clients)), inline=False)
            embed.add_field(name="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", value="Author: {} | [OfficialServer]({}) | [OfficialWebSite]({})".format(self.info["AUTHOR"], self.info["SERVER_URL"], self.info["WEB_URL"]), inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["f"])
    async def feedback(self, ctx, *, text):
        channel = self.bot.get_channel(self.info["ERROR_CHANNEL"])
        embed = discord.Embed(title="お問い合わせ", description="サーバー:{0.name}({0.id})\nチャンネル:{1.name}({1.id})\nユーザー:{2}({2.id})".format(ctx.guild, ctx.channel ,ctx.author))
        embed.add_field(name="内容:", value=text, inline=False)
        embed.add_field(name="お問い合わせID:", value=ctx.message.id)
        embed.set_footer(text=datetime.datetime.now().strftime('%Y年%m月%d日 %H時%M分'))
        msg = await channel.send(embed=embed)
        try:
            await ctx.send(":white_check_mark:お問い合わせが完了しました.\n内容によってはBOT管理者がお返事を公式サーバーにて掲示いたします.\n貴重なご意見ありがとうございました。\nお問い合わせID: {}".format(ctx.message.id))
        except:
            await ctx.send(":white_check_mark: Your inquiry is complete.\nDepending on the content, the BOT administrator will post a reply on the official server.\nThank you for your valuable feedback.\nFeedback ID: {}".format(ctx.message.id))

    @commands.command(aliases=["chk"])
    async def check(self, ctx, text):
        pass


def setup(bot):
    bot.add_cog(Other(bot))