from typing import Any
from public_setting.variable import Tier
import numpy as np
from ER_datas.id_characterName import LoadCharacter
import json
import re
from ER_apis.crawler import DakPlayerCrawler
from public_setting.function import Json
import os
from ER_datas.tier_mmr import *
from ER_apis.crawler import *
import scipy.stats as stats


calculater = ["/", "*", "+", "-", "(", ")", "%", "//"]


def _split_caclulater(name: str = "") -> list:
    _dic = {}
    _n = 0
    _change = 0
    for i in name:
        if i in calculater:
            _changed = 1
        else:
            _changed = 2
        if _change != _changed:
            _n += 1
            _change = _changed
        _dic[_n] = _dic.get(_n, "") + i
    return _dic


class User:
    def __init__(self, user_name, season=12, update=False, save=True) -> None:
        self.user_name = user_name
        self.season = season
        self.save = save
        if update:
            self.user_data = self.crawling()
        else:
            response = self.open_DB()
            if not response.get(400):
                self.user_data = response
            else:
                self.user_data = self.crawling()

    def open_DB(self):
        db_dir = os.environ.get("DB_DIR", "./datas")
        root_dir = f"{db_dir}/user/{self.user_name}.json"
        return Json().read(root_dir)

    def crawling(self):
        craw = DakPlayerCrawler(self.user_name, self.season)
        craw.crawling_mmr_change()
        if self.save:
            craw.save()
        return craw.datas


class DataClass:
    def __init__(self, *conditions):
        self.conditions = conditions

    def add_data(self, user_data):
        print("not add_data")

    def user_count(self):
        try:
            self.user_count_num += 1
        except:
            self.user_count_num = 0

    def add_data_game_id(self):
        print("not add_data_game_id")

    def game_count(self):
        try:
            self.game_count_num += 1
        except:
            self.game_count_num = 0

    def last_calculate(self):
        print("not last_calculate")


class TestClass(DataClass):
    def __init__(self):
        self.count_add_data = 0
        self.count_add_data_game_id = 0
        self.count_last_calculate = 0
        self.user_data = []

    def add_data(self, user_data):
        self.count_add_data += 1
        self.user_data = user_data

    def add_data_game_id(self):
        self.count_add_data_game_id += 1

    def last_calculate(self):
        self.count_last_calculate += 1


class DicCharacterFilterData(DataClass):
    def __init__(self, *condition):
        self.dic_characterNum_datas = {}
        self.condition = condition

    def add_data(self, user_data):
        characterNum = user_data["characterNum"]
        datas = {}
        list_request_datatype = self.condition
        for request_datatype in list_request_datatype:
            datas[request_datatype] = user_data[request_datatype]
        self.dic_characterNum_datas[characterNum] = self.dic_characterNum_datas.get(
            characterNum, []
        ) + [datas]


class DicCharacterData(DataClass):
    def __init__(self, *condition):
        self.dic_characterNum_datas = {}
        self.condition = condition

    def add_data(self, user_data):
        characterNum = user_data["characterNum"]
        datas = {}
        conditions = self.condition
        db = self.dic_characterNum_datas.get(characterNum, {})
        for condition in conditions:
            db[condition] = db.get(condition, []) + [user_data[condition]]
        self.dic_characterNum_datas[characterNum] = db


class ListFilterData(DataClass):
    def __init__(self, *conditions, **name_dic):
        """
        1.must name_dic.value not in conditions
        2. only */+-()//
        """
        self.name_dic = name_dic
        self.conditions = {}
        for condition in conditions:
            self.conditions[name_dic.get(condition, condition)] = []

    def add_data(self, user_data):
        filter_name = list(self.name_dic.values())
        # 기본 condition
        for condition in self.conditions:
            if condition not in filter_name:
                self.conditions[condition] += [user_data.get(condition, 0)]
        # 계산 condition
        for condition_caculate in self.name_dic:
            # condition_list = re.split(re_caculater, condition_caculate)
            condition_dic = _split_caclulater(condition_caculate)
            condition_str = ""
            for index in condition_dic.values():
                if index.isdigit() or index in calculater:
                    condition_str += index
                else:
                    condition_str += str(user_data[index])
            self.conditions[self.name_dic[condition_caculate]] += [eval(condition_str)]


'''
class ForeignTeam(DataClass):
    def __init__(self, *conditions):
        self.conditions = set([*conditions, "mmrBefore", "mmrGainInGame"])
        self.team = {
            "domestic_team": self._team_db_setting(),
            "foreigner_team": self._team_db_setting(),
        }
        self.memory = {}
        self._memory_reset()

    def _team_db_setting(self):
        db = {}
        db["tier"] = Tier()
        for condition in self.conditions:
            db[condition] = []

        return db

    def _memory_reset(self):
        for i in range(1, 9):
            memory_i = {}
            memory_i["state"] = 0
            memory_i["language"] = ""
            for condition in self.conditions:
                memory_i[condition] = []
            self.memory[i] = memory_i

    def add_data(self, user_data):
        # 입력 내용
        teamNumber = user_data["teamNumber"]
        memory = self.memory[teamNumber]

        """미확인"""
        _language = user_data.get("language", "error")
        if memory["state"] == 0:
            memory["language"] = _language
        elif memory["language"] != _language:
            memory["state"] = -1

        for condition in self.conditions:
            memory[condition] += [user_data[condition]]
        if memory["state"] != -1:
            memory["state"] += 1

    def add_data_game_id(self):
        for team_id in self.memory:
            if self.memory[team_id]["state"] == 3:
                self._add_team_data("domestic_team", self.memory[team_id])
            elif self.memory[team_id]["state"] == -1:
                self._add_team_data("foreigner_team", self.memory[team_id])
            else:
                pass

        self._memory_reset()

    def _add_team_data(self, key, memory):
        team = self.team[key]
        for team_mate in range(0, 3):
            team["tier"].split_tier(
                memory["mmrBefore"][team_mate], memory["mmrGainInGame"][team_mate]
            )
        for condition in self.conditions:
            team[condition] += [*memory[condition]]

    def last_calculate(self):
        print("last_calcu")
        teams = self.team
        for team in teams:
            print("team", team)
            teams[team]["tier"].mean()
'''


# 이모티콘 소통의 유의미 한가?(현 mmr, 획득 mmr)
class EmoticonMMRClass(DataClass):
    def __init__(self, split_range: int, *condition):
        self.dic_mmr_emoticon = {}
        self.split_range = split_range
        self.condition = condition

    def add_data(self, user_data):
        datas = {}
        user_mmr = int(user_data["mmrBefore"] / self.split_range) * self.split_range
        if self.dic_mmr_emoticon.get(user_mmr) == None:
            datas[user_mmr] = []
        else:
            datas[user_mmr] = self.dic_mmr_emoticon[user_mmr]
        self.dic_mmr_emoticon[user_mmr] = datas[user_mmr] + [
            {
                "emoticon_count": user_data["useEmoticonCount"],
                "gained_mmr": user_data["mmrGain"],
            }
        ]

    def last_calculate(self):
        data = {"sum": {}, "mean": {}}
        for mmr in self.dic_mmr_emoticon:
            emoticon_count = int(
                sum(data["emoticon_count"] for data in self.dic_mmr_emoticon[mmr])
            )
            gained_mmr = sum(data["gained_mmr"] for data in self.dic_mmr_emoticon[mmr])
            data["sum"][mmr] = {
                "emoticon_count": emoticon_count,
                "gained_mmr": gained_mmr,
            }
            data["mean"][mmr] = {
                "emoticon_count": emoticon_count / len(self.dic_mmr_emoticon[mmr]),
                "gained_mmr": gained_mmr / len(self.dic_mmr_emoticon[mmr]),
            }
        return data

    def get_data(self):
        return self.dic_mmr_emoticon

    # 보안 콘솔을 자주 키는 험체(탱커, 딜러)


class CharacterClass(DataClass):
    def __init__(self, *condition):
        self.dic_characterNum_datas = {"tanker": 0, "dealer": 0, "support": 0}
        self.dic_character_class = {}
        self.dic_characterNum_datas_list = {"tanker": [], "dealer": [], "support": []}
        with open("setting/class.json", "r", encoding="utf-8") as class_json_file:
            self.dic_character_class = json.load(class_json_file)
        self.condition = condition

    def add_data(self, user_data):
        character_name = LoadCharacter()
        characterNum = user_data["characterNum"]
        str_user_character_name = character_name[str(characterNum)]
        str_user_character_class = "dealer"
        if str_user_character_name in self.dic_character_class["tanker"]:
            str_user_character_class = "tanker"
        elif str_user_character_name in self.dic_character_class["support"]:
            str_user_character_class = "support"
        used_security_console = user_data["useSecurityConsole"]
        datas = used_security_console
        self.dic_characterNum_datas[str_user_character_class] = (
            self.dic_characterNum_datas[str_user_character_class] + datas
        )
        self.dic_characterNum_datas_list[str_user_character_class].append(datas)

    def last_calculate(self):
        datas = {}
        for class_key in self.dic_characterNum_datas_list:
            datas[class_key] = np.mean(self.dic_characterNum_datas_list[class_key])
        self.dic_characterNum_mean_datas = datas
        self.dic_characterNum_percentage_datas = {
            "tanker": self.dic_characterNum_datas["tanker"]
            / int(sum(self.dic_characterNum_datas.values())),
            "dealer": self.dic_characterNum_datas["dealer"]
            / int(sum(self.dic_characterNum_datas.values())),
            "support": self.dic_characterNum_datas["support"]
            / int(sum(self.dic_characterNum_datas.values())),
        }
        return datas

    def get_percentage(self):
        return self.dic_characterNum_percentage_datas

    def get_mean(self):
        return self.dic_characterNum_mean_datas

    def get_data(self):
        return self.dic_characterNum_datas_list


# #카메라 통합
class Camera_All(DataClass):
    def __init__(self, *condition):
        self.condition = condition
        self.dic_cameraGroup_mmr = {}
        self.dic_cameraGroup_tier = {}
        self.dic_cameraGroup_Rank = {}
        self.dic_cameraGroup_LukeMai = {"나머지": []}
        self.tier_range = {}
        self.tier_range[0] = "아이언"
        self.tier_range[1000] = "브론즈"
        self.tier_range[2000] = "실버"
        self.tier_range[3000] = "골드"
        self.tier_range[4000] = "플레티넘"
        self.tier_range[5000] = "다이아"
        self.tier_range[6000] = "데미갓"
        self.tier_range["all"] = "all"

    def add_data(self, user_data):
        # #총 카메라 수
        addScamera = user_data["addSurveillanceCamera"]
        addTcamera = user_data["addTelephotoCamera"]
        addCamera = addTcamera + addScamera
        # #카메라 설치 수에 따른 mmr 증가량
        mmrGainIngame = user_data["mmrGainInGame"]
        self.dic_cameraGroup_mmr[addCamera] = self.dic_cameraGroup_mmr.get(
            addCamera, []
        ) + [mmrGainIngame]

        # #티어 별 카메라 설치 평균
        mmrBefore = user_data["mmrBefore"]
        if mmrBefore > 6000:
            mmrBefore = 6000
        mmrBefore_thousand = (mmrBefore % 10000 // 1000) * 1000
        tier = self.tier_range[mmrBefore_thousand]
        self.dic_cameraGroup_tier[tier] = self.dic_cameraGroup_tier.get(tier, []) + [
            addCamera
        ]

        # #등수 별 카메라 설치 평균
        gameRank = user_data["gameRank"]
        self.dic_cameraGroup_Rank[gameRank] = self.dic_cameraGroup_Rank.get(
            gameRank, []
        ) + [addCamera]

        # #루크/마이의 카메라 설치 평균
        character_name = LoadCharacter()
        characterNum = user_data["characterNum"]
        str_characterNum = str(characterNum)
        if characterNum == 22:
            self.dic_cameraGroup_LukeMai[
                character_name[str_characterNum]
            ] = self.dic_cameraGroup_LukeMai.get(
                character_name[str_characterNum], []
            ) + [
                addCamera
            ]
        elif characterNum == 45:
            self.dic_cameraGroup_LukeMai[
                character_name[str_characterNum]
            ] = self.dic_cameraGroup_LukeMai.get(
                character_name[str_characterNum], []
            ) + [
                addCamera
            ]
        else:
            self.dic_cameraGroup_LukeMai["나머지"].append(addCamera)

    def last_calculate(self):
        # #카메라 설치 수에 따른 mmr 증가량
        for key in self.dic_cameraGroup_mmr:
            self.dic_cameraGroup_mmr[key] = np.mean(self.dic_cameraGroup_mmr[key])
        self.dic_cameraGroup_mmr = dict(
            sorted(self.dic_cameraGroup_mmr.items(), key=lambda x: x[0])
        )

        # #티어 별 카메라 설치 평균
        for tier in self.dic_cameraGroup_tier:
            self.dic_cameraGroup_tier[tier] = np.mean(self.dic_cameraGroup_tier[tier])
        rank_order = [
            "아이언",
            "브론즈",
            "실버",
            "골드",
            "플레티넘",
            "다이아",
            "데미갓",
        ]
        self.dic_cameraGroup_tier = {
            key: value
            for key, value in sorted(
                self.dic_cameraGroup_tier.items(), key=lambda x: rank_order.index(x[0])
            )
        }

        # #등수 별 카메라 설치 평균
        for gameRank in self.dic_cameraGroup_Rank:
            self.dic_cameraGroup_Rank[gameRank] = np.mean(
                self.dic_cameraGroup_Rank[gameRank]
            )
        self.dic_cameraGroup_Rank = dict(
            sorted(self.dic_cameraGroup_Rank.items(), key=lambda x: x[0])
        )

        # #루크/마이의 카메라 설치 평균 수
        for character in self.dic_cameraGroup_LukeMai:
            self.dic_cameraGroup_LukeMai[character] = np.mean(
                self.dic_cameraGroup_LukeMai[character]
            )


# #티어별 하이퍼루프
class Hyperloop(DataClass):
    def __init__(self, *condition):
        self.condition = condition
        self.dic_Hyperloop_tier = {}
        self.tier_range = {}
        self.tier_range[0] = "아이언"
        self.tier_range[1000] = "브론즈"
        self.tier_range[2000] = "실버"
        self.tier_range[3000] = "골드"
        self.tier_range[4000] = "플레티넘"
        self.tier_range[5000] = "다이아"
        self.tier_range[6000] = "데미갓"
        self.tier_range["all"] = "all"

    def add_data(self, user_data):
        useHyperLoop = user_data["useHyperLoop"]
        mmrBefore = user_data["mmrBefore"]
        if mmrBefore > 6000:
            mmrBefore = 6000
        mmrBefore_thousand = (mmrBefore % 10000 // 1000) * 1000
        tier = self.tier_range[mmrBefore_thousand]
        self.dic_Hyperloop_tier[tier] = self.dic_Hyperloop_tier.get(tier, []) + [
            useHyperLoop
        ]

    def last_calculate(self):
        for tier in self.dic_Hyperloop_tier:
            self.dic_Hyperloop_tier[tier] = np.mean(self.dic_Hyperloop_tier[tier])
        rank_order = [
            "아이언",
            "브론즈",
            "실버",
            "골드",
            "플레티넘",
            "다이아",
            "데미갓",
        ]
        self.dic_Hyperloop_tier = {
            key: value
            for key, value in sorted(
                self.dic_Hyperloop_tier.items(), key=lambda x: rank_order.index(x[0])
            )
        }


class GetMMRFromRankByTier(DataClass):
    def __init__(self, *conditions):
        super().__init__(*conditions)
        self.conditions = ["gameRank", "mmrBefore", "mmrGainInGame"]
        self._mmrRank = {1: 40, 2: 25, 3: 20, 4: 10, 5: 5, 6: 5}
        self._tier = {
            0: "아이언",
            1: "브론즈",
            2: "실버",
            3: "골드",
            4: "플레티넘",
            5: "다이아",
            6: "미스릴~",
        }
        self.datas = {}
        self.datas["mmrRank"] = []
        self.datas["mmrGainInGame"] = []
        self.datas["Tier"] = []
        self.datas["gameRank"] = []

    def add_data(self, user_data):
        self.datas["gameRank"].append(user_data["gameRank"])
        self.datas["mmrRank"].append(self._mmrRank.get(user_data["gameRank"], 0))
        self.datas["mmrGainInGame"].append(user_data["mmrGainInGame"])
        self.datas["Tier"].append(
            self._tier.get(user_data["mmrBefore"] // 1000, "미스릴~")
        )


class GetMMRFromRank(DataClass):
    def __init__(self, *conditions):
        super().__init__(*conditions)
        self.conditions = ["gameRank", "mmrBefore", "mmrGainInGame"]
        self._mmrRank = {1: 40, 2: 25, 3: 20, 4: 10, 5: 5, 6: 5}
        self.datas = {}
        self.datas["mmrRank"] = []
        self.datas["mmrGainInGame"] = []
        self.datas["mmrBefore_range250"] = []
        self.datas["gameRank"] = []
        self.range_list = {}

    def add_data(self, user_data):
        self.datas["gameRank"].append(user_data["gameRank"])
        self.datas["mmrRank"].append(self._mmrRank.get(user_data["gameRank"], 0))
        self.datas["mmrGainInGame"].append(user_data["mmrGainInGame"])
        range_name = (user_data["mmrBefore"] // 250) * 250
        self.datas["mmrBefore_range250"].append(range_name)
        self.range_list[range_name] = None

    def last_calculate(self):
        self.range_list = list(self.range_list.keys())


class TeamLuck(DataClass):
    def __init__(self, player_name, season, *conditions):
        self.conditions = conditions
        self.dic_TeamKill_tier = {
            "아이언": [],
            "브론즈": [],
            "실버": [],
            "골드": [],
            "플레티넘": [],
            "다이아": [],
            "데미갓": [],
        }
        self.dic_rank_tier = {
            "아이언": [],
            "브론즈": [],
            "실버": [],
            "골드": [],
            "플레티넘": [],
            "다이아": [],
            "데미갓": [],
        }
        self.user = User(player_name, season)
        self.grade = []

    def add_data(self, user_data):
        mmrBefore = user_data["mmrBefore"]
        gameRank = user_data["gameRank"]
        TeamKill = user_data["teamKill"]
        for i in range(len(tier)):
            if mmrBefore <= tier[i]:
                mmrBefore = tier[i]
                break
            elif mmrBefore >= 6200:
                mmrBefore = 6200
        self.dic_TeamKill_tier[tier_range[mmrBefore]].append(TeamKill)
        self.dic_rank_tier[tier_range[mmrBefore]].append(gameRank)

    def last_calculate(self):
        user_TeamKill = self.user.user_data["TK"]
        user_mmr = self.user.user_data["MMR"][-1]
        user_rank = self.user.user_data["RANK"]
        user_rank = [int(i[1:]) for i in user_rank if re.match(r"#[0-9]+", i)]

        for i in range(len(tier)):
            if user_mmr <= tier[i]:
                user_mmr = tier[i]
                break
            elif user_mmr >= 6200:
                user_mmr = 6200

        mean_user_TeamKill = np.mean(user_TeamKill)
        mean_user_rank = np.mean(user_rank)
        mean_TeamKill = np.mean(self.dic_TeamKill_tier[tier_range[user_mmr]])
        mean_rank = np.mean(self.dic_rank_tier[tier_range[user_mmr]])
        std_TeamKill = np.std(self.dic_TeamKill_tier[tier_range[user_mmr]])
        std_rank = np.std(self.dic_rank_tier[tier_range[user_mmr]])
        normal_dist_TeamKill = stats.norm(mean_TeamKill, std_TeamKill)
        normal_dist_rank = stats.norm(mean_rank, std_rank)
        rank_persent = 100 * (1 - normal_dist_rank.cdf(mean_user_rank))
        TeamKill_persent = 100 * (1 - normal_dist_TeamKill.cdf(mean_user_TeamKill))
        print(tier_range[user_mmr])
        print(len(self.dic_TeamKill_tier[tier_range[user_mmr]]))
        Grade(TeamKill_persent, self.grade)
        Grade(rank_persent, self.grade)
        dic_print = {
            "해당 티어 평균 팀킬": mean_TeamKill,
            "당신의 평균 팀킬 ": mean_user_TeamKill,
            "당신의 상위 팀킬 퍼센트(%) ": TeamKill_persent,
            "당신의 상위 평균 순위 퍼센트(%)": rank_persent,
        }
        print(dic_print)
        print(self.grade)
        mean_grade = np.mean(self.grade)
        if 1 <= mean_grade < 2:
            print("통나무2개드는자")
        elif 2 <= mean_grade < 3:
            print("통나무1개드는자")
        elif 3 <= mean_grade < 4:
            print("1인분초과2인분미만")
        elif 4 <= mean_grade < 5:
            print("1인분")
        elif 5 <= mean_grade < 6:
            print("통나무주의보")
        elif 6 <= mean_grade < 7:
            print("통나무1개")
        elif 7 <= mean_grade < 8:
            print("통나무2개")
        else:
            print("탭댄스")
