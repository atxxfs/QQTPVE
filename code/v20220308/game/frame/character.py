import pygame
from game.const import color as C

CHARACTER_IMG_ROOT = "res/img/"
CHARACTER_ORIENTS = ("STAND_R", "STAND_U", "STAND_L", "STAND_D", "R", "U", "L", "D", "LOSE")
CHARACTER_COMPONENTS = {
    "R": ("Leg", "Leg_m", "Body", "Cloth", "Cloth_m", "Face", "Hair", "Hair_m", "Cap", "Cap_m", "Fhadorn", "Npack", "Npack_m"),
    "U": ("Leg", "Leg_m", "Body", "Cloth", "Cloth_m", "Face", "Hair", "Hair_m", "Cap", "Cap_m", "Fhadorn", "Npack", "Npack_m"),
    "L": ("Leg", "Leg_m", "Body", "Cloth", "Cloth_m", "Npack", "Npack_m", "Face", "Hair", "Hair_m", "Cap", "Cap_m", "Fhadorn"),
    "D": ("Npack", "Npack_m", "Leg", "Leg_m", "Body", "Cloth", "Cloth_m", "Face", "Hair", "Hair_m", "Cap", "Cap_m", "Fhadorn")
}
CHARACTER_COMPONENTS_MASKED = ("Cloth_m", "Hair_m", "Leg_m", "Npack_m", "Cap_m")
characters = {}


# 通过name和color获取body序列。
# name是一级键，取自body_json的NAME；color是二级键，取自color常量
def get_character(character_json, color):
    name = character_json["NAME"]
    if name not in characters.keys():
        characters[name] = dict()
    if color not in characters[name]:
        a_color = load_color(character_json, color)
        characters[name][color] = a_color
    return characters[name][color]


# 通过color常量和body_json创建body序列，用于生成get_body的二级键的值
def load_color(character_json, color):
    a_color = {}
    # 遍历朝向
    for orient in CHARACTER_ORIENTS:
        if orient not in character_json.keys():
            # 如果character没有这个方向，则跳过不加载
            continue
        a_color[orient] = dict()
        a_color[orient]["Len"] = size = character_json[orient]["Len"]  # 获取每个朝向的帧数
        a_color[orient]["Cx"] = character_json[orient]["Cx"]  # 获取每个朝向的x偏移
        a_color[orient]["Cy"] = character_json[orient]["Cy"]  # 获取每个朝向的y偏移
        # 遍历身体部件
        for component in CHARACTER_COMPONENTS["D"]:
            if component not in character_json[orient].keys():
                # 如果character没有这个组件，则跳过不加载
                continue
            a_color[orient][component] = list()
            type = component.lower()
            frames = character_json[orient][component]
            # 对于每一帧 加载图片
            for i in range(size):
                # print(CHARACTER_IMG_ROOT + type + '/' + frames["IMG"][i])
                img = pygame.image.load(CHARACTER_IMG_ROOT + type + '/' + frames["IMG"][i]).convert_alpha()
                if component in CHARACTER_COMPONENTS_MASKED:
                    # 对MASK图层进行颜色转换
                    surf = pygame.Surface(img.get_size())
                    surf.fill(color[0])
                    img.blit(surf, (0, 0), special_flags=pygame.BLEND_ADD)
                    surf.fill(color[1])
                    img.blit(surf, (0, 0), special_flags=pygame.BLEND_SUB)
                cx = frames["CX"][i]
                cy = frames["CY"][i]
                a_color[orient][component].append(Frame(img, cx, cy))
    return a_color


class Frame:

    def __init__(self, image: pygame.Surface, cx, cy):
        self.image = image
        self.cx = cx
        self.cy = cy
