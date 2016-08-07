from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now


class Character(models.Model):
    name = models.CharField(max_length=64)
    skills = models.ManyToManyField('CharSkill', related_name='learned_by')
    total_sp = models.BigIntegerField()
    standings = models.ManyToManyField('Standing', related_name='standing_to')
    last_update = models.DateTimeField(default=now)
    password = models.CharField(max_length=64, blank=True)
    unspent_skillpoints = models.IntegerField(default=0)
    remaps = models.IntegerField(default=0)


class NPC_Corp(models.Model):
    name = models.CharField(max_length=256)


class Standing(models.Model):
    corp = models.ForeignKey(NPC_Corp)
    value = models.DecimalField(max_digits=4, decimal_places=2)


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
    last_update = models.DateTimeField(default=now)
    blacklisted = models.BooleanField()
    thread_text = models.CharField(max_length=6000, null=True)
    thread_title = models.CharField(max_length=100)
    thread_id = models.IntegerField()
    character = models.ForeignKey(Character, null=True)
    title_history = models.ManyToManyField('ThreadTitle', related_name='previous_titles')


class ThreadTitle(models.Model):
    title = models.CharField(max_length=500)
    date = models.DateTimeField(default=now)
