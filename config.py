import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

assert BOT_TOKEN, "BOT_TOKEN not found in environment variables"


LOC_KW_DICT = {"干燥平原：萨兰火山口": "Saraan",
               "哈维泽：渎神旷野": "Desecration",
               "肯基斯坦：灼热盆地": "Basin",
               "索格伦：卡恩·艾达": "Adar",
               "破碎群峰：炼狱场": "Crucible"}


BOSS_KW_DICT = {"贪魔，诅咒之金": "Avarice",
                "阿煞魃，疫魔": "Ashava",
                "徘徊死魔，死亡赋予生命": "Death"}


LOCATION_DICT = {"干燥平原：萨兰火山口": "the Saraan Caldera, Dry Steppes",
                 "哈维泽：渎神旷野": "Fields of Desecration, Hawezar",
                 "肯基斯坦：灼热盆地": "Seared Basin, Kehjistan",
                 "索格伦：卡恩·艾达": "Caen Adar, Scosglen",
                 "破碎群峰：炼狱场": "the Crucible, Fractured Peaks"}


BOSS_DICT = {"贪魔，诅咒之金": "Avarice",
             "阿煞魃，疫魔": "Ashava",
             "徘徊死魔，死亡赋予生命": "The Wandering Death"}
