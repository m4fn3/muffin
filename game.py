# import
from discord.ext import commands, tasks
import asyncio, discord, json, os , random, sys, time, traceback2


class Game(commands.Cog):

    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        with open("./INFO.json") as F:
            info = json.load(F)
        self.info = info
        with open("./DATABASE.json") as F:
            database = json.load(F)
        self.database = database
        self.load_roles()
        with open("./correct.json") as F:
            correct = json.load(F)
        self.correct = correct

    def load_roles(self):
        with open("./ROLE.json") as F:
            roles = json.load(F)
        self.ADMIN = roles["ADMIN"]
        self.Contributor = roles["Contributor"]
        self.BAN = roles["BAN"]

    def save_database(self):
        with open("./DATABASE.json", 'w') as F:
            json.dump(self.database, F, indent=2)

    def initialize_data(self, user_id):
        self.database[str(user_id)] = {
            "best_score" : 30,
            "single" : {
                "all_matches" : 0,
                "win_matches" : 0
            },
            "multi" : {
                "all_matches" : 0,
                "win_matches" : 0
            }
        }

    async def cog_before_invoke(self, ctx):
        self.load_roles()
        if ctx.author.id in self.BAN:
            if str(ctx.guild.region) == "japan":
                await ctx.send(":warning:`あなたはBANされているため,使用できません.\n異議申し立ては公式サーバーにてお願いします.`")
                raise commands.CommandError("Your Account Banned")
            else:
                await ctx.send(":warning:`You cannnot use because you are banned.\nFor objection please use Official Server.`")
                raise commands.CommandError("Your Account Banned")

    @commands.command(aliases=["r"])
    async def rule(self, ctx):
        embed = discord.Embed(title="Rule Of Shadow Choice (1/3)")
        embed.set_image(url="{}Tehon.jpg".format(self.info["PICT_URL"]))
        embed.add_field(name="基本", value="```これらは頭の片隅に覚えておく必要のある5つのアイテムです.\n今から説明する2つのルールにあったアイテムをこの中から選ぶことになります.\nこれらは問題の下部にリアクションとして表示されます.\nまた各問題の右上にも表示されるので適宜参照してください.\n(注意)色鉛筆は2色を持ちます.オレンジ色と黄色は同じ1つの色(黄色)とみなします.\nではその二つのルールを説明します!```")
        await ctx.send(embed=embed)
        embed = discord.Embed(title="Rule Of Shadow Choice (2/3)")
        embed.set_thumbnail(url="{}Tehon.jpg".format(self.info["PICT_URL"]))
        embed.set_image(url="{}/main/1.jpg".format(self.info["PICT_URL"]))
        embed.add_field(name="ルール1", value="```表示された絵の中に上で示した５つのうちのどれかが同じ色で入っている場合それが正解です!\nすかさずそのアイテムのリアクションをおしましょう.```", inline=False)
        embed.add_field(name="例1", value="```この場合絵の中に名刺が同じ色(紫)でうつっているので紫の名刺のリアクションが正解です.```", inline=False)
        await ctx.send(embed=embed)
        embed = discord.Embed(title="Rule Of Shadow Choice (3/3)")
        embed.set_thumbnail(url="{}Tehon.jpg".format(self.info["PICT_URL"]))
        embed.set_image(url="{}/main/11.jpg".format(self.info["PICT_URL"]))
        embed.add_field(name="ルール2", value="```カードの中に正しい色で写っているモノがなければ(ルール1を満たすものがなければ)、\n色も種類も絵に映っていないアイテムをとりましょう.```", inline=False)
        embed.add_field(name="例2", value="```この場合絵の中に正しい色でうつっているものはないので,色も種類も絵に写っていないものを探します.\nはさみ,緑,黄,えんぴつがだめなので,'黄'のノート,赤い'はさみ','緑'のメジャー,青の'鉛筆'はダメです.\nよって残った紫のメジャーが正解です.```", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["st"])
    async def status(self, ctx):
        self.load_roles()
        if ctx.message.mentions == []:
            embed = discord.Embed(title="ステータス")
            embed.set_thumbnail(url=ctx.author.avatar_url)
            if ctx.author.id in self.ADMIN:
                embed.add_field(name="ユーザーー情報", value="```yaml\nユーザー:{}\nユーザーID:{}\n[管理者]```".format(ctx.author, ctx.author.id), inline=False)
            elif ctx.author.id in self.Contributor:
                embed.add_field(name="ユーザーー情報", value="```fix\nユーザー:{}\nユーザーID:{}\n[貢献者]```".format(ctx.author, ctx.author.id), inline=False)
            else:
                embed.add_field(name="ユーザーー情報", value="```ユーザー:{}\nユーザーID:{}```".format(ctx.author, ctx.author.id), inline=False)
            if str(ctx.author.id) in self.database:
                embed.add_field(name="ShadowChoice", value="```c\n最短正答時間:{}\nシングルスコア:\n  全試合数:{}\n  勝利試合数:{}\n  勝率:{}%\nマルチスコア:\n  全試合数:{}\n  勝利試合数:{}\n  勝率:{}%```".format(self.database[str(ctx.author.id)]["best_score"], self.database[str(ctx.author.id)]["single"]["all_matches"], self.database[str(ctx.author.id)]["single"]["win_matches"], round(self.database[str(ctx.author.id)]["single"]["win_matches"]/self.database[str(ctx.author.id)]["single"]["all_matches"]*100 ,2) ,self.database[str(ctx.author.id)]["multi"]["all_matches"], self.database[str(ctx.author.id)]["multi"]["win_matches"], round(self.database[str(ctx.author.id)]["multi"]["win_matches"]/self.database[str(ctx.author.id)]["multi"]["all_matches"]*100 ,2)))
            else:
                embed.add_field(name="ShadowChoice", value="```まだプレイしていません.```")
            await ctx.send(embed=embed)
        else:
            target = ctx.message.mentions[0]
            embed = discord.Embed(title="ステータス")
            embed.set_thumbnail(url=target.avatar_url)
            if target.id in self.ADMIN:
                embed.add_field(name="ユーザーー情報", value="```yaml\nユーザー:{}\nユーザーID:{}\n[管理者]```".format(target, target.id), inline=False)
            elif target.id in self.Contributor:
                embed.add_field(name="ユーザーー情報", value="```fix\nユーザー:{}\nユーザーID:{}\n[貢献者]```".format(target, target.id), inline=False)
            else:
                embed.add_field(name="ユーザーー情報", value="```ユーザー:{}\nユーザーID:{}```".format(target, target.id), inline=False)
            if str(target.id) in self.database:
                embed.add_field(name="ShadowChoice", value="```c\n最短正答時間:{}\nシングルスコア:\n  全試合数:{}\n  勝利試合数:{}\n  勝率:{}%\nマルチスコア:\n  全試合数:{}\n  勝利試合数:{}\n  勝率:{}%```".format(self.database[str(target.id)]["best_score"], self.database[str(target.id)]["single"]["all_matches"], self.database[str(target.id)]["single"]["win_matches"], round(self.database[str(target.id)]["single"]["win_matches"]/ self.database[str(target.id)]["single"]["all_matches"]*100 ,2) ,self.database[str(target.id)]["multi"]["all_matches"], self.database[str(target.id)]["multi"]["win_matches"], round(self.database[str(target.id)]["multi"]["win_matches"]/self.database[str(target.id)]["multi"]["all_matches"]*100 ,2)))
            else:
                embed.add_field(name="ShadowChoice", value="```まだプレイしていません.```")
            await ctx.send(embed=embed)

    @commands.command(aliases=["sc"])
    async def shadowchoice(self, ctx):
        try:
            msg_list = ctx.message.content.split()
            mode: int
            afk = 0
            is_right: int
            if len(msg_list) == 1:
                mode = 1
                round_time = 1
            elif len(msg_list) > 3:
                return await ctx.send(":warning:コマンドが間違っています.正しい構文: `{}play [人数] [試合数]`".format(self.info["PREFIX"]))
            elif len(msg_list) == 2:
                if not msg_list[1].isdigit():
                    return await ctx.send(":warning:人数は整数で指定してください.")
                elif int(msg_list[1]) < 1:
                    return await ctx.send(":warning:人数は0以下にはなりません.")
                else:
                    mode = int(msg_list[1])
                    round_time = 1
            else:
                if (not msg_list[1].isdigit()) or (not msg_list[2].isdigit()):
                    return await ctx.send(":warning:コマンドが間違っています.人数やラウンド数は整数で指定してください.")
                elif (int(msg_list[1]) < 1) or (int(msg_list[2]) < 1):
                    return await ctx.send(":warning:コマンドが間違っています.人数やラウンド数は0以下にはなりません.")
                else:
                    mode = int(msg_list[1])
                    round_time = int(msg_list[2])
            if mode == 1:
                if str(ctx.author.id) not in self.database:
                    self.initialize_data(ctx.author.id)
                for i in range(round_time):
                    embed = discord.Embed(title="Wait 5 sec...")
                    embed.add_field(name="お待ちください", value="`約5秒後に開始されます!`")
                    org_msg = await ctx.send(embed=embed)
                    await org_msg.add_reaction(self.info["SCnotebook"])
                    await org_msg.add_reaction(self.info["SCmajor"])
                    await org_msg.add_reaction(self.info["SCscissors"])
                    await org_msg.add_reaction(self.info["SCCard"])
                    await org_msg.add_reaction(self.info["SCPencil"])
                    ch = ctx.message.channel
                    ah = ctx.message.author
                    num = str(random.randint(1,25))
                    num_id = self.correct[num]
                    def check(r, u):
                        return u == ah and r.message.channel == ch and r.message.id == org_msg.id and r.emoji.id in self.info["SC"]
                    embed = discord.Embed(title="Question of Shadow Choice ({}/{})".format(i+1, round_time))
                    embed.set_thumbnail(url="{}Tehon.jpg".format(self.info["PICT_URL"]))
                    embed.set_image(url="{}/main/{}.jpg".format(self.info["PICT_URL"], num))
                    embed.add_field(name="問題", value="下のリアクションを押して回答してください!")
                    await org_msg.edit(embed=embed)
                    pstart = time.time()
                    try:
                        preaction, puser = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                        elapsed_time = time.time() - pstart
                        if preaction.emoji.id == num_id:
                            await ctx.send("{}あなたは正解しました!".format(self.info["SCmaru"]))
                            is_right = 1
                        else:
                            await ctx.send("{}あなたは間違いました!".format(self.info["SCbatu"]))
                            is_right = 0
                        elapsed_time = round(elapsed_time, 2)
                        embed = discord.Embed(title="Question of Shadow Choice ({}/{})".format(i+1, round_time))
                        embed.add_field(name="終了済", value="試合はすでに終了しています.")
                        await org_msg.edit(embed=embed)
                        if is_right == 1:
                            embed = discord.Embed(title="Result of Shadow Choice ({}/{})".format(i+1, round_time))
                            embed.add_field(name="結果発表", value="```正解者:{}\n計測時間:{}[s]```".format(puser.display_name, elapsed_time))
                            await ctx.send(embed=embed)
                            if self.database[str(puser.id)]["best_score"] > elapsed_time:
                                self.database[str(puser.id)]["best_score"] = elapsed_time
                                await ctx.send("{} <@{}>さん!ベストスコア更新!\nあなたのスコア:{}[s]".format(self.info["SCcongr"], puser.id, elapsed_time))
                            self.database[str(puser.id)]["single"]["win_matches"] += 1
                        else:
                            embed = discord.Embed(title="Result of Shadow Choice ({}/{})".format(i+1, round_time))
                            embed.add_field(name="結果発表", value="```正解者:なし\n計測時間:{}[s]```".format(elapsed_time))
                            await ctx.send(embed=embed)
                        self.database[str(puser.id)]["single"]["all_matches"] += 1
                        self.save_database()
                        afk = 0
                    except asyncio.TimeoutError:
                        elapsed_time = time.time() - pstart
                        elapsed_time = round(elapsed_time, 2)
                        await ctx.send("{}回答できた人がいなかったため,この問題を終了します.".format(self.info["SCwarning"]))
                        embed = discord.Embed(title="Result of Shadow Choice")
                        embed.add_field(name="結果発表", value="```正解者:なし\n時間:{}[s]```".format(elapsed_time))
                        await org_msg.edit(embed=embed)
                        afk += 1
                        if afk == 2:
                            await ctx.send("{}2回連続で回答がなかったためこの部屋を終了します.".format(self.info["SCwarning"]))
                            break
            else:
                embed = discord.Embed(title="Join to match of Shadow Choice")
                members = []
                go_vote = []
                ch = ctx.message.channel
                embed.add_field(name="参加画面", value="```diff\n以下のリアクションを押して参加してください!\n+ 参加\n- 参加をキャンセル\n定員に達し次第ゲームが開始されます\n定員人数:{}人```".format(mode))
                join_msg = await ctx.send(embed=embed)
                def check(r, u):
                    return r.message.channel == ch and r.message.id == join_msg.id and r.emoji.id in self.info["PM"] and u != self.bot.user
                await join_msg.add_reaction(self.info["SCplus"])
                await join_msg.add_reaction(self.info["SCminus"])
                await join_msg.add_reaction(self.info["SCgoanyway"])
                while len(members) < mode:
                    try:
                        preaction, puser = await self.bot.wait_for("reaction_add", timeout=30.0 ,check=check)
                        if preaction.emoji.id == 717595208757280890:
                            if puser.id not in members:
                                members.append(puser.id)
                                await ctx.send("{}<@{}>さんが参加しました.".format(self.info["SCmaru"], puser.id))
                            else:
                                await ctx.send("{}<@{}>さんは既に参加しています.".format(self.info["SCwarning"], puser.id))
                        elif preaction.emoji.id == 717595196665102348:
                            if puser.id in members:
                                members.remove(puser.id)
                                await ctx.send("{}<@{}>さんの参加をキャンセルしました.".format(self.info["SCbatu"], puser.id))
                            else:
                                await ctx.send("{}<@{}>さんは参加していません.".format(self.info["SCwarning"], puser.id))
                        elif preaction.emoji.id == 718028499163807785:
                            if (puser.id not in go_vote) and (puser.id in members):
                                go_vote.append(puser.id)
                                await ctx.send("{}<@{}>さんが強制的にスタートに投票しました.({}/2)".format(self.info["SCmaru"], puser.id, len(go_vote)))
                                if len(go_vote) == 2:
                                    await ctx.send("{} 2人が強制的にスタートに投票したため{}人モードに変更します.".format(self.info["SCcheck"], len(members)))
                                    mode = len(members)
                                    break
                            elif puser.id in go_vote:
                                await ctx.send("{}<@{}>さんは既に強制的にスタートに投票しています.({}/2)".format(self.info["SCwarning"], puser.id, len(go_vote)))
                            else:
                                await ctx.send("{}<@{}>さんは参加していないので投票できません!".format(self.info["SCwarning"], puser.id))
                    except asyncio.TimeoutError:
                        return await ctx.send("{} 一定時間反応がなかったためセッションを終了しました.".format(self.info["SCwarning"]))
                embed = discord.Embed(title="Join to match of Shadow choice")
                embed.add_field(name="参加できません", value="試合はすでに開始されています.")
                await join_msg.edit(embed=embed)
                await ctx.send("{} 定員に達したためゲームを開始します!".format(self.info["SCcheck"]))
                for i in members:
                    if str(i) not in self.database:
                        self.initialize_data(i)
                for i in range(round_time):
                    embed = discord.Embed(title="Wait 5 sec...")
                    embed.add_field(name="お待ちください", value="`約5秒後に開始されます!`")
                    org_msg = await ctx.send(embed=embed)
                    await org_msg.add_reaction(self.info["SCnotebook"])
                    await org_msg.add_reaction(self.info["SCmajor"])
                    await org_msg.add_reaction(self.info["SCscissors"])
                    await org_msg.add_reaction(self.info["SCCard"])
                    await org_msg.add_reaction(self.info["SCPencil"])
                    ch = ctx.message.channel
                    ah = ctx.message.author
                    num = str(random.randint(1,25))
                    num_id = self.correct[num]
                    answered_members = []
                    elapsed_time = 30
                    end_code = 0
                    right_ppl = None
                    def check(r, u):
                        return r.message.channel == ch and r.message.id == org_msg.id and r.emoji.id in self.info["SC"] and u.id in members
                    embed = discord.Embed(title="Question of Shadow Choice ({}/{})".format(i+1, round_time))
                    embed.set_thumbnail(url="{}Tehon.jpg".format(self.info["PICT_URL"]))
                    embed.set_image(url="{}/main/{}.jpg".format(self.info["PICT_URL"], num))
                    embed.add_field(name="問題", value="下のリアクションを押して回答してください!")
                    await org_msg.edit(embed=embed)
                    pstart = time.time()
                    while len(answered_members) < mode:
                        try:
                            preaction, puser = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
                            elapsed_time = time.time() - pstart
                            if puser.id not in answered_members:
                                if preaction.emoji.id == num_id:
                                    await ctx.send("{}<@{}>さん!あなたは正解しました!".format(self.info["SCmaru"],puser.id))
                                    right_ppl = str(puser.id)
                                    end_code = 1
                                    break
                                else:
                                    await ctx.send("{}<@{}>さん!あなたは間違いました!\nこの試合であなたはこれ以上回答できません!\n次のラウンドをお待ちください.".format(self.info["SCbatu"],puser.id))
                                    answered_members.append(puser.id)
                            else:
                                await ctx.send("{}<@{}>さん!あなたはすでに間違っているためこれ以上回答できません!\n次のラウンドをお待ちください.".format(self.info["SCwarning"],puser.id))
                        except asyncio.TimeoutError:
                            end_code = 2
                            await ctx.send("{} 一定時間反応がなかったためセッションを終了しました".format(self.info["SCwarning"]))
                            break
                    embed = discord.Embed(title="Question of Shadow Choice ({}/{})".format(i+1, round_time))
                    embed.add_field(name="終了済", value="試合はすでに終了しています.")
                    await org_msg.edit(embed=embed)
                    if end_code == 0:
                        embed = discord.Embed(title="Result of Shadow Choice ({}/{})".format(i+1, round_time))
                        players = ""
                        for mem in members:
                            players += "\n<@{}>".format(mem)
                        embed.add_field(name="結果発表", value="`正解者はいませんでした、、、\n`参加者:`{}".format(players))
                        await ctx.send(embed=embed)
                        afk = 0
                    elif end_code == 1:
                        embed = discord.Embed(title="Result of Shadow Choice ({}/{})".format(i+1, round_time))
                        elapsed_time = round(elapsed_time, 2)
                        players = ""
                        for mem in members:
                            players += "\n<@{}>".format(mem)
                        embed.add_field(name="結果発表", value="`正解者:`<@{}>\n`参加者:`{}\n`正解者の計測時間:`{}[s]".format(right_ppl, players,elapsed_time))
                        await ctx.send(embed=embed)
                        afk = 0
                        if self.database[right_ppl]["best_score"] > elapsed_time:
                            self.database[right_ppl]["best_score"] = elapsed_time
                            await ctx.send("{} <@{}>さん!ベストスコア更新!\nあなたのスコア:{}[s]".format(self.info["SCcongr"], right_ppl, elapsed_time))
                        self.database[right_ppl]["multi"]["win_matches"] += 1
                    elif end_code == 2:
                        embed = discord.Embed(title="Result of Shadow Choice ({}/{})".format(i+1, round_time))
                        players = ""
                        for mem in members:
                            players += "\n<@{}>".format(mem)
                        embed.add_field(name="結果発表", value="`全員どこかへ行ってしまったようです、、、`\n`参加者:`{}".format(players))
                        await ctx.send(embed=embed)
                        afk += 1
                        if afk == 2:
                            await ctx.send("{}2回連続で回答がなかったためこの部屋を終了します.".format(self.info["SCwarning"]))
                            break
                    for mem in members:
                        self.database[str(mem)]["multi"]["all_matches"] += 1
                    self.save_database()
        except:
            await ctx.send(traceback2.format_exc())


def setup(bot):
    bot.add_cog(Game(bot))
