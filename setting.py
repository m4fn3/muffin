
from discord.ext import commands
import asyncio, discord, io, json, os, pprint, random, re, sys, time, traceback2
from identifier import *


class Setting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        with open("./INFO.json") as F:
            info = json.load(F)
        self.info = info

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

    async def send_text(self, ctx, code, arg1=None, arg2=None, force_region=False):
        if force_region:
            lang = get_language(LanguageCode.CHANNEL.value, ctx.guild.region)
        else:
            lang = get_language(self.bot.database[str(ctx.author.id)]["language"], ctx.guild.region)
        embed: discord.Embed
        if code == "YOUR_ACCOUNT_BANNED":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(":warning:`あなたはBANされているため,使用できません.\n異議申し立ては公式サーバーにてお願いします.`")
                raise commands.CommandError("Your Account Banned")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(":warning:`You cannnot use because you are banned.\nFor objection please use Official Server.`")
                raise commands.CommandError("Your Account Banned")
        elif code == "MAINTENANCE":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(":warning:`現在メンテナンス中です.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(":warning:`Currently under maintenance.")
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
        elif code == "WRONG_LANGUAGE":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(f":warning:`言語が間違っています.対応言語は`{self.bot.PREFIX}lang_list`で確認できます.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(f":warning:`Wrong language.To check supported language, type `{self.bot.PREFIX}lang_list")
        elif code == "MUSICINFO_ON":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(":white_check_mark:`音楽の再生メッセージをオンにしました.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(":white_check_mark:`Turned on the music play message.`")
        elif code == "MUSICINFO_OFF":
            if lang == LanguageCode.JAPANESE:
                await ctx.send(":white_check_mark:`音楽の再生メッセージをオフにしました.`")
            elif lang == LanguageCode.ENGLISH:
                await ctx.send(":white_check_mark:`Turned off the music play message.`")

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
            await channel.send(embed=embed, file=discord.File(fp=io.StringIO(message), filename="error.txt"))

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
        if self.bot.maintenance and ctx.author.id not in self.bot.ADMIN:
            await self.send_text(ctx, "MAINTENANCE", force_region=True)
            raise commands.CommandError("MAINTENANCE")
        if str(ctx.author.id) not in self.bot.database:
            await self.init_database(ctx)
        if ctx.author.id in self.bot.BAN:
            await self.send_text(ctx, "YOUR_ACCOUNT_BANNED")
            raise commands.CommandError("Your Account Banned")

    @commands.command(aliases=["lang", "lg"])
    async def language(self, ctx, *, lang):
        if lang.lower() in ["ch", "channel", "server", "guild", "region", "チャンネル", "サーバー", "地域"]:
            self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.CHANNEL.value
            if str(ctx.guild.region) == "japan":
                await ctx.send(":white_check_mark:`言語を[サーバー地域]に設定しました!`")
            else:
                await ctx.send(":white_check_mark:`Changed language to [Server Region]!`")
        elif lang.lower() in ["ja", "jp", "japanese", "japan", "日本語", "日本"]:
            self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.JAPANESE.value
            await ctx.send(":white_check_mark:`言語を[日本語]に設定しました!`")
        elif lang.lower() in ["en", "eng", "english", "英語"]:
            self.bot.database[str(ctx.author.id)]["language"] = LanguageCode.ENGLISH.value
            await ctx.send(":white_check_mark:`Changed language to [English]!`")
        else:
            await self.send_text(ctx, "WRONG_LANGUAGE")

    @commands.command(aliases=["mi"])
    async def musicinfo(self, ctx):
        if self.bot.database[str(ctx.author.id)]["music"]["play_message"]:
            self.bot.database[str(ctx.author.id)]["music"]["play_message"] = False
            await self.send_text(ctx, "MUSICINFO_OFF")
        else:
            self.bot.database[str(ctx.author.id)]["music"]["play_message"] = True
            await self.send_text(ctx, "MUSICINFO_ON")


def setup(bot):
    bot.add_cog(Setting(bot))