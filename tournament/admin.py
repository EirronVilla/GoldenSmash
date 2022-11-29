from django.contrib import admin
from .models import Match, Journey, Player, PlayerMatch
# Register your models here.


admin.site.register(Journey)
admin.site.register(Match)
admin.site.register(Player)
admin.site.register(PlayerMatch)
