import urllib.request as url_
import json
import discord
from math import sqrt, floor
from datetime import datetime as dt, timedelta as td
from dateutil import tz
from operator import itemgetter
from matplotlib import pyplot as plt
import numpy as np


token = "NjY5Njg1Njg4NTAwODc5Mzkw.XlvByA.qjU7ylNdDzQgBYLQk_BfojITiso"
key = "e91ba361-3ad8-4083-8bb6-9c57fb97c4d6"
blood_guild_id = "53c81676ed50878f4ccc75be"
guild_id = "5988f8340cf2851f860c9a7b"

# https://api.hypixel.net/player?key=de9ba88a-bf47-4244-a762-eef7e4a806ba&name=MMeisterr
# https://api.hypixel.net/guild?key=e91ba361-3ad8-4083-8bb6-9c57fb97c4d6&id=5988f8340cf2851f860c9a7b
#
# print(guild_member_list(guild_data))
# player_data = json.loads(str(url_.urlopen(player_url).read(), 'utf-8'))
guild_url = f"https://api.hypixel.net/guild?key={key}&id={guild_id}"
guild_data = json.loads(str(url_.urlopen(guild_url).read(), 'utf-8'))
d = dt.today() - td(weeks=520)
global_w_start = dt(2009, 7, 31, 0, 0)
color = 0x009500


def name_from_uuid(uuid):
    fixed = uuid.replace("-", "")
    url = f"https://api.mojang.com/user/profiles/{fixed}/names"
    return json.loads(str(url_.urlopen(url).read(), 'utf-8'))


def uuid_from_name(name):
    url = f"https://api.mojang.com/users/profiles/minecraft/{name}"
    return json.loads(str(url_.urlopen(url).read(), 'utf-8'))["id"]


def guild_member_list(data):
    guild_list = []
    for c, uuid in enumerate(data["guild"]["members"], start=1):
        try:
            member = Member(name_from_uuid(uuid["uuid"])[-1]["name"])
            guild_list.append(member)
        except TypeError:
            print("F")
        print(c, name_from_uuid(uuid["uuid"])[-1]["name"])
    return guild_list


def player_data_from_name(name):
    player_url = f"https://api.hypixel.net/player?key={key}&name={name}"
    return json.loads(str(url_.urlopen(player_url).read(), 'utf-8'))


def find_guild(name):
    uuid = uuid_from_name(name)
    findguild_url = f"https://api.hypixel.net/findguild?key={key}&byUuid={uuid}"
    print(findguild_url)
    guild = json.loads(str(url_.urlopen(findguild_url).read(), 'utf-8'))
    print(guild)



def xp_to_lvl(n):
    a = -1250
    b = -8750
    lvl = (-b-sqrt(b**2 - 4*a*n))/(2*a)
    return floor(lvl * 100)/100.0 + 1


def lvl_to_xp(n):
    if n <= 1000:
        xp = 0
        for i in range(1, n):
            xp += (i * 2500) + 7500
        return xp
    else:
        return None


class Member:
    def __init__(self, name):
        self.data = player_data_from_name(name)
        self.name = self.data["player"]["displayname"]
        self.xp = self.data["player"]["networkExp"]
        self.nw_level = xp_to_lvl(self.xp)
        try:
            self.quests = self.data["player"]["achievements"][
                "general_quest_master"]
        except KeyError:
            self.quests = 0
        self.ap = self.data["player"]["achievementPoints"]
        try:
            self.bw_fd = self.data["player"]["stats"]["Bedwars"][
                "final_deaths_bedwars"]
        except KeyError:
            self.bw_fd = 1
        try:
            self.bw_fkdr = round(
                self.data["player"]["stats"]["Bedwars"]["final_kills_bedwars"] /
                self.bw_fd, 2)
        except KeyError:
            self.bw_fkdr = 0
        self.bw_level = self.data["player"]["achievements"]["bedwars_level"]
        self.bw_wins = self.data["player"]["achievements"]["bedwars_wins"]
        self.duel_wins = self.set_duel_("wins")
        self.duel_losses = self.set_duel_("losses")
        try:
            self.duel_wlr = [float(
                (self.duel_wins[k]) / self.duel_losses[k]) / 2.33
                             for k in self.duel_losses]
        except ZeroDivisionError:
            self.duel_wlr = [float(self.duel_wins[k]) / 2.33
                             for k in self.duel_losses]
        try:
            self.bb_score = self.data["player"]["stats"]["BuildBattle"]["score"]
        except KeyError:
            self.bb_score = 0
        try:
            self.sw_xp = self.data["player"]["stats"]["SkyWars"][
                "skywars_experience"]
            self.sw_wins = self.data["player"]["achievements"][
                               "skywars_wins_team"] + self.data[
                "player"]["achievements"]["skywars_wins_solo"]
            self.sw_kills = self.data["player"]["achievements"][
                               "skywars_kills_team"] + self.data[
                "player"]["achievements"]["skywars_kills_solo"]
        except KeyError:
            self.sw_xp = 0
            self.sw_wins = 0
            self.sw_kills = 0
        try:
            self.uhc_score = self.data["player"]["stats"]["UHC"]["score"]
        except KeyError:
            self.uhc_score = 0
        try:
            self.mm_wins = self.data["player"]["stats"]["MurderMystery"]["wins"]
        except KeyError:
            self.mm_wins = 0
        achs = self.data["player"]["achievements"]
        try:
            bs_wins = achs["tntgames_bow_spleef_wins"]
            tr_wins = achs["tntgames_bow_spleef_wins"]
            tt_wins = achs["tntgames_tnt_tag_wins"]
            tw_wins = achs["tntgames_wizards_wins"]
            pr_wins = achs["tntgames_pvp_run_wins"]
            self.tnt_wins = bs_wins + tr_wins + tt_wins + tw_wins + pr_wins
        except KeyError:
            self.tnt_wins = 0

    def __repr__(self):
        return self.name

    def key_error(self, a, b):
        try:
            return self.data["player"]["stats"]["Duels"][f"{b}_{a}"]
        except KeyError:
            return 0

    def set_duel_(self, a):
        sumo = self.key_error(a, "sumo_duel")
        bg_s = self.key_error(a, "bridge_duel")
        bg_d = self.key_error(a, "bridge_doubles")
        bg_f = self.key_error(a, "bridge_four")
        uhc_s = self.key_error(a, "uhc_duel")
        uhc_d = self.key_error(a, "uhc_doubles")
        sw_s = self.key_error(a, "sw_duel")
        sw_d = self.key_error(a, "sw_doubles")
        return {"sumo": sumo, "bridge": bg_s + bg_d + bg_f,
                "uhc": uhc_s + uhc_d, "sw": sw_s + sw_d}

    def check(self):
        meet = 0
        meets = dict()
        if self.bw_level >= 150 and self.bw_fkdr >= 5:
            meets["bw"] = [True, 1]
            meet += 1
        else:
            meets["bw"] = [False, round(min(self.bw_level / 150,
                                            self.bw_fkdr / 5), 3)]
        ratios = [i for i in [self.duel_wins["sumo"] / 3500,
                              self.duel_wins["bridge"] / 2000,
                              self.duel_wins["uhc"] / 2500,
                              self.duel_wins["sw"] / 2500]]
        meets["duels"] = [False, 0]
        l = list(zip(ratios, self.duel_wlr))
        for i in l:
            if i[0] >= 1 and i[1] >= 1:
                meets["duels"] = [True, 1]
                meet += 1
        if meets["duels"][0] is False:
            meets["duels"] = [False, max([min(i) for i in l])]
        if self.bb_score >= 8000:
            meets["bb"] = [True, 1]
            meet += 1
        else:
            meets["bb"] = [False, self.bb_score / 8000]
        if self.sw_xp >= 45000:
            meets["sw"] = [True, 1]
            meet += 1
        else:
            meets["sw"] = [False, self.sw_xp / 45000]
        if self.uhc_score >= 210:
            meets["uhc"] = [True, 1]
            meet += 1
        else:
            meets["uhc"] = [False, self.uhc_score / 210]
        if self.mm_wins >= 2000:
            meets["mm"] = [True, 1]
            meet += 1
        else:
            meets["mm"] = [False, self.mm_wins / 2000]
        if self.tnt_wins >= 1000:
            meets["tnt"] = [True, 1]
            meet += 1
        else:
            meets["tnt"] = [False, self.tnt_wins / 1000]
        meets["meet"] = meet
        return meets


'''
d = dict()
for i in guild_data["guild"]["members"]:
    name = name_from_uuid(i["uuid"])[-1]["name"]
    print(name)
    try:
            member = Member(name)
    except:
        pass
    d[name] = member.check()["meet"]
        

for j, i in enumerate(sorted(
    d.items(), key=itemgetter(1), reverse=True), start=1):
    print(f"{j}. {i[0]}: {i[1]}")
'''

'''
def apdata(name):
    ap = list()
    apd = list()
    user = Member(name)
    for k in user.data["player"]["achievementRewardsNew"].keys():
        ap.append(k.replace("for_points_", ""))
    for v in user.data["player"]["achievementRewardsNew"].values():
        apd.append(dt.fromtimestamp(v//1000))
    return apd, ap
d = apdata("Dungeon")
d2 = apdata("Iaan")
plt.scatter(d[0], d[1], s=1)
plt.scatter(d2[0], d2[1], s=1)
plt.plot(d[0], d[1])
plt.plot(d2[0], d2[1])
plt.yticks(5 * np.arange(round(len(d2[1])) / 5))
plt.show()
reno = Member("Renolest")
mm = Member("MMeisterr")
ap = list()
for i in mm.data["player"]["achievementsOneTime"]:
    if i not in reno.data["player"]["achievementsOneTime"]:
        ap.append(i)
print(ap)

'''

client = discord.Client()


@client.event
async def on_message(message):
    print(f"{message.author}: {message.content}")
    if message.content.find("!reqs") != -1:
        try:
            a = Member(message.content.replace("!reqs ", ""))
            d = a.check()
            k = list(d.keys())
            v = list(d.values())
            embd = discord.Embed(title=f"{k[0]}",
                                 description=f"{v[0][0]} ("
                                 f"{round(100 * v[0][1], 2)}%)", color=color)
            embd.set_author(name=f"{a.name} (nw level {a.nw_level})")
            for i in range(1, 7):
                embd.add_field(name=f"{k[i]}",
                               value=f"{v[i][0]} ({round(100 * v[i][1], 2)}%)",
                               inline=False)
        except TypeError:
            embd = discord.Embed(title="User not found.")
    elif message.content.find("!quests") != -1:
        today = dt.now(tz=tz.gettz('America/New_York'))
        d_start = dt(today.year, today.month, today.day)
        week = (dt.now() - global_w_start).days // 7
        w_start = global_w_start + td(weeks=week)
        try:
            a = Member(message.content.replace("!quests ", ""))
            try:
                quests = a.data["player"]["quests"]
            except KeyError:
                quests = dict()
            weekly = 0
            daily = 0
            for q in quests.keys():
                try:
                    last = quests[q]["completions"][-1]["time"]
                    if "weekly" in q:
                        if dt.fromtimestamp(last//1000) > w_start:
                            weekly += 1
                    else:
                        if dt.fromtimestamp(last//1000) > d_start:
                            daily += 1
                except KeyError:
                    pass
            embd = discord.Embed(title="Total quests",
                                 description=f"{a.quests}", color=color)
            embd.set_author(name=f"{a.name}")
            embd.add_field(name="Daily quests",
                           value=f"{daily}/73", inline=True)
            embd.add_field(name="Weekly quests",
                           value=f"{weekly}/36", inline=True)
        except TypeError:
            embd = discord.Embed(title="User not found.")
    elif message.content.find("!ap") != -1:
        try:
            a = Member(message.content.replace("!ap ", ""))
            embd = discord.Embed(title=f"{a.name} has {a.ap} "
                                       f"achievement points.")
        except TypeError:
            embd = discord.Embed(title="User not found.")
    elif message.content.find("!xp") != -1:
        try:
            a = Member(message.content.split()[2])
            try:
                xp = lvl_to_xp(int(message.content.split()[1]))
                xp_needed = f"{max(xp - a.xp, 0):,}"
                embd = discord.Embed(title="Total xp",
                                     description=f"{a.xp:,}", color=color)
                embd.set_author(name=f"{a.name} (nw level {a.nw_level})")
                embd.add_field(name="Needed xp",
                               value=xp_needed, inline=True)
            except ValueError and TypeError:
                embd = discord.Embed(title="Wrong Usage of the command.")
        except TypeError:
            embd = discord.Embed(title="User not found.")
    elif message.content.find("!gxp ") != -1:
        try:
            a = uuid_from_name(message.content.replace("!gxp ", ""))
            found = False
            for i in guild_data["guild"]["members"]:
                if a == i["uuid"]:
                    found = True
                    name = name_from_uuid(a)[-1]["name"]
                    c = 0
                    for j in i["expHistory"].items():
                        c += j[1]
                    embd = discord.Embed(title="Last 7 days guild experience", description=f"{c:,}", color=color)
                    embd.set_author(name=f"{name}")
                    for j in i["expHistory"].items():
                        embd.add_field(name=j[0],
                                       value=f"{j[1]:,}", inline=False)
            if found is False:
                embd = discord.Embed(title="This player is not in Enigmata.")
        except json.decoder.JSONDecodeError:
            embd = discord.Embed(title="User not found.")
    elif message.content.find("!top") != -1:
        check, title, reverse = 0, str(), None
        if message.content.find("first") != -1:
            check = 1
            title = "Top 25 with the most gxp"
            reverse = True
        if message.content.find("last") != -1:
            check = -1
            title = "Top 25 with the least gxp"
            reverse = False
        if check != 0:
            d = {}
            for i in guild_data["guild"]["members"]:
                name = i["uuid"]
                gxp = 0
                for j in i["expHistory"].items():
                    gxp += j[1]
                d[name] = gxp
            c = 0
            embd = discord.Embed(title=title, description="last 7 days.", color=color)
            msg = await client.send_message(message.channel, content="0/25")
            for j, i in enumerate(sorted(
                    d.items(), key=itemgetter(1), reverse=reverse), start=1):
                name = name_from_uuid(i[0])[-1]["name"]
                embd.add_field(name=f"{j}. {name}", value=f"{i[1]:,}", inline=False)
                c += 1
                await client.edit_message(msg, new_content=f"{c}/25")
                if c == 25:
                    await client.delete_message(msg)
                    break
            embd.set_author(name="ENIGMATA")
        else:
            embd = discord.Embed(title="Wrong Usage of the command.")

    try:
        await client.send_message(message.channel, content=None, embed=embd)
    except UnboundLocalError:
        pass

client.run(token)

