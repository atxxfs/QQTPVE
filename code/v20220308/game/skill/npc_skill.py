import pygame


class NpcSkill:

    def __init__(self, user, to, skill_instances):
        self.user = user
        self.to = to
        self.skill_instances = skill_instances
        self.time_init = pygame.time.get_ticks()
        self.current_time = pygame.time.get_ticks()
        self.base_skills = list()
        self.load()

    def load(self):
        self.skill_instances.append(self)

    def update(self):
        self.current_time = pygame.time.get_ticks()
        for a_base_skill_info in self.base_skills:
            if a_base_skill_info[3] and self.current_time - self.time_init > a_base_skill_info[1]:
                pass

    def add_base_skill(self, a_base_skill, time_from, time_to):
        self.base_skills.append([a_base_skill, time_from, time_to, True])

    def create_base_skill_instance(self, a_base_skill):
        pass


class HeiLongDistantFire5x5(NpcSkill):

    def __init__(self, user, to, skill_instances):
        super().__init__(user, to, skill_instances)

    def load(self):
        super().load()
