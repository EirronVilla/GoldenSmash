from django.db import models

class Player(models.Model):
    nickname = models.CharField(max_length=100)
    def __str__(self):
        return self.nickname

class Journey(models.Model):
    date = models.DateField()
    number = models.IntegerField(default=0)
    isActive = models.BooleanField(default=True)
    JourneyType = models.CharField(max_length=50, blank=True, null=True, default="Journey")

    def __str__(self):
        return "Jornada " + str(self.id)

class Match(models.Model):
    win = models.ForeignKey(Player, related_name="winner", on_delete=models.CASCADE)
    second = models.ForeignKey(Player, related_name="second", on_delete=models.CASCADE)
    number = models.IntegerField(default=0)
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    wasPlayed = models.BooleanField(default=True)

    def __str__(self):
        return "Partida " + str(self.id)

class PlayerMatch(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    kills = models.IntegerField(blank=True, null=True)
    damage = models.IntegerField(blank=True, null=True)
    role = models.CharField(max_length=15, default="Player")

