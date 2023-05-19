"""GoldenSmash URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tournament import views as tournament_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', tournament_views.register, name='register'),
    path('summary/', tournament_views.sumredirect, name='summary'),
    path('summary/<nickname>/', tournament_views.summary, name='default'),
    path('journeys/<nickname>/', tournament_views.journeys, name='journeys'),
    path('createJourney/<nickname>/', tournament_views.createJourney, name='createJourney'),
    path('journey/<nickname>/<id>', tournament_views.journey, name='journey'),
    path('closeJourney/<nickname>/<id>', tournament_views.closeJourney, name='closeJourney'),
    path('closeTournament/<nickname>/<id>', tournament_views.closeTournament, name='closeTournament'),
    path('tournament/rankings/<nickname>', tournament_views.closeJourney, name='tournamentRankings'),
    path('tournaments/<nickname>', tournament_views.tournamentList, name='tournament'),
    path('tournaments/<nickname>/<id>', tournament_views.tournament, name='tournament'),
    path('nextRound/<nickname>/<id>/<matchesDisplayed>', tournament_views.nextRount, name='nextRount'),
]
