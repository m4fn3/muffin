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
        self.filter, self.filter_list = self.get_filter()
        self.black_link_filter, self.black_link_list, self.white_link_filter, self.white_link_list = self.get_link_filter()
        self.save_link_list.start()

    def get_filter(self):
        binary_dict: str
        with open("./filter_words.txt") as F:
            binary_dict = F.read()
        decoded_dict = ''.join(chr(int(x, 2)) for x in binary_dict.split())
        filter_dict = json.loads(decoded_dict)
        filter_list = filter_dict["words"]
        filter_text = "|".join(filter_list)
        return filter_text, filter_list

    def get_link_filter(self):
        link_dict: dict
        with open("./filter_links.json") as F:
            link_dict = json.load(F)
        print(link_dict)
        black_link_list = link_dict["black_list"]
        black_link_filter = "|".join(black_link_list)
        white_link_list = link_dict["white_list"]
        white_link_filter = "|".join(white_link_list)
        print(black_link_filter, black_link_list, white_link_filter, white_link_list)
        return black_link_filter, black_link_list, white_link_filter, white_link_list

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

    @tasks.loop(seconds=30.0)
    async def save_link_list(self):
        pass
        #with open("./link_list.json", 'w') as db:
        #    json.dump(self.link_list, db, indent=2)


def setup(bot):
    bot.add_cog(GlobalChat(bot))






