from discord.ext import commands, tasks
import discord, json, traceback2, re
from chat_filter import *


class GlobalChat(commands.Cog):

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        with open("./INFO.json") as F:
            info = json.load(F)
        self.info = info
        self.channel_match = "\<\#(?P<channel_id>[0-9]{18})\>"
        self.filter = ""
        self.filter_list = None
        self.black_link_filter = ""
        self.black_link_list = []
        self.white_link_filter = ""
        self.white_link_list = []
        self.init_filter()

    def init_filter(self):
        binary_dict: str
        with open("./filter_words.txt") as F:
            binary_dict = F.read()
        decoded_dict = ''.join(chr(int(x, 2)) for x in binary_dict.split())
        filter_dict = json.loads(decoded_dict)
        self.filter_list = filter_dict
        link_dict: dict
        with open("./filter_links.json") as F:
            link_dict = json.load(F)
        self.black_link_list = link_dict["black_list"]
        self.white_link_list = link_dict["white_list"]
        self.update_filter()

    def save_filter(self):
        link_dict = {
            "white_list": self.white_link_list,
            "black_list": self.black_link_list
        }
        with open("./filter_links.json", "w") as F:
            json.dump(link_dict, F, indent=2)
        filter_str = json.dumps(self.filter_list)
        filter_binary = ' '.join(format(ord(letter), 'b') for letter in filter_str)
        with open("./filter_words.txt", "w") as F:
            F.write(filter_binary)
        self.update_filter()

    def update_filter(self):
        self.black_link_filter = "|".join(self.black_link_list)
        self.white_link_filter = "|".join(self.white_link_list)
        self.filter = "|".join(self.filter_list)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        if payload.channel_id in self.bot.global_chat["general"]:
            if payload.message_id in self.bot.global_chat_log:
                for message in self.bot.global_chat_log[payload.message_id]["webhooks"]:
                    await message.delete()

    async def on_global_message(self, message):
        try:
            if message.author.id in self.bot.BAN:
                return
            new_filter = Filter(self.filter, self.black_link_filter, self.white_link_filter)
            return_code = await new_filter.execute_filter(message.content)
            if return_code == 1:
                return await message.add_reaction("🚫")
            else:
                await message.add_reaction("✅")
            self.bot.global_chat_log[message.id] = {
                "sender": str(message.author),
                "sender_id": message.author.id,
                "guild": message.guild.id,
                "channel": message.channel.id,
                "content": message.content,
                "attachments": [],
                "attachments_count": 0,
                "webhooks": []
            }
            files = []
            for attachment in message.attachments:
                attached_file = await attachment.to_file()
                files.append(attached_file)
                self.bot.global_chat_log[message.id]["attachments"].append(attachment.proxy_url)
            self.bot.global_chat_log[message.id]["attachments_count"] = len(files)
            for global_channel_id in self.bot.global_chat["general"]:
                if global_channel_id == message.channel.id:
                    continue
                global_channel = self.bot.get_channel(global_channel_id)
                if global_channel is None:
                    self.bot.global_chat["general"].remove(global_channel_id)
                    with open("./GLOBAL_CHAT.json", 'w') as db:
                        json.dump(self.bot.global_chat, db, indent=2)
                    continue
                channel_webhooks = await global_channel.webhooks()
                webhook = discord.utils.get(channel_webhooks, name="muffin-webhook")
                if webhook is None:
                    webhook = await global_channel.create_webhook(name="muffin-webhook")
                files = []
                for attachment in message.attachments:
                    attached_file = await attachment.to_file()
                    files.append(attached_file)
                msg_obj = await webhook.send(message.content, username=message.author.name, avatar_url=message.author.avatar_url, files=files, wait=True)
                self.bot.global_chat_log[message.id]["webhooks"].append(msg_obj)
        except:
            await message.channel.send(traceback2.format_exc())

    @commands.command(aliases=["g", "global"])
    async def global_chat(self, ctx):
        try:
            text = ctx.message.content.split(" ", 1)
            channel_id: int
            if len(text) == 1:
                channel_id = ctx.channel.id
            else:
                result = re.search(self.channel_match, text[1])
                if result is None:
                    return await ctx.send("チャンネルを検出できませんでした")
                else:
                    matched_channel_id = int(result["channel_id"])
                    channel = discord.utils.get(ctx.guild.text_channels, id=matched_channel_id)
                    if channel is None:
                        return await ctx.send("チャンネルを検出できませんでした")
                    channel_id = channel.id
            if channel_id in self.bot.global_chat["general"]:
                return await ctx.send("すでにグローバルチャットに登録されているチャンネルです")
            self.bot.global_chat["general"].append(channel_id)
            with open("./GLOBAL_CHAT.json", 'w') as db:
                json.dump(self.bot.global_chat, db, indent=2)
            await ctx.send(f"<#{channel_id}>チャンネルをグローバルチャットに追加しました.")
        except:
            await ctx.send(traceback2.format_exc())

    @commands.group()
    async def word(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("word <add|remove|show> <text>")

    @word.command(name="add", aliases=["a"])
    async def word_add(self, ctx, *, text):
        if text not in self.filter_list:
            self.filter_list.append(text)
            self.save_filter()
            await ctx.send(f"{text} を単語リストに追加しました.")
        else:
            await ctx.send(f"{text} はすでに単語リストに登録されています.")

    @word.command(name="delete", aliases=["remove", "d", "r"])
    async def word_delete(self, ctx, *, text):
        if text in self.filter_list:
            self.filter_list.remove(text)
            self.save_filter()
            await ctx.send(f"{text} を単語リストから削除しました.")
        else:
            await ctx.send(f"{text} は単語リストに登録されていません.")

    @commands.group()
    async def whitelist(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("whitelist <add|remove|show> <text>")

    @whitelist.command(name="add", aliases=["a"])
    async def whitelist_add(self, ctx, *, text):
        if text not in self.white_link_list:
            self.white_link_list.append(text)
            self.save_filter()
            await ctx.send(f"{text} をURLホワイトリストリストに追加しました.")
        else:
            await ctx.send(f"{text} はすでにURLホワイトリストに登録されています.")

    @whitelist.command(name="delete", aliases=["remove", "d", "r"])
    async def whitelist_delete(self, ctx, *, text):
        if text in self.white_link_list:
            self.white_link_list.remove(text)
            self.save_filter()
            await ctx.send(f"{text} をURLホワイトリストから削除しました.")
        else:
            await ctx.send(f"{text} はURLホワイトリストに登録されていません.")

    @commands.group()
    async def blacklist(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("blacklist <add|remove|show> <text>")

    @blacklist.command(name="add", aliases=["a"])
    async def blacklist_add(self, ctx, *, text):
        if text not in self.black_link_list:
            self.black_link_list.append(text)
            self.save_filter()
            await ctx.send(f"{text} をURLブラックリストに追加しました.")
        else:
            await ctx.send(f"{text} はすでにURLブラックリストに登録されています.")

    @blacklist.command(name="delete", aliases=["remove", "d", "r"])
    async def blacklist_delete(self, ctx, *, text):
        if text in self.black_link_list:
            self.black_link_list.remove(text)
            self.save_filter()
            await ctx.send(f"{text} をURLブラックリストから削除しました.")
        else:
            await ctx.send(f"{text} はURLブラックリストに登録されていません.")


def setup(bot):
    bot.add_cog(GlobalChat(bot))






