from django.db import models


class Character(models.Model):
    name = models.CharField(max_length=64)
    skills = models.ManyToManyField('CharSkill',related_name='learned_by')
    total_sp = models.IntegerField()

class Skill(models.Model):
    name = models.CharField(max_length=64)
    typeID = models.IntegerField()
    groupID = models.IntegerField()
    groupName = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    rank = models.SmallIntegerField()

class CharSkill(models.Model):
    character = models.ForeignKey(Character)
    skill_points = models.IntegerField()
    level = models.IntegerField()
    skill = models.ForeignKey(Skill)

class Thread(models.Model):
    last_update = models.DateTimeField()
    blacklisted = models.BooleanField()
    thread_text = models.CharField(max_length=6000,null=True)
    thread_title = models.CharField(max_length=100)
    thread_id = models.IntegerField()
    character = models.ForeignKey(Character,null=True)
