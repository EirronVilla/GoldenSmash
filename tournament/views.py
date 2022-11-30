from django.shortcuts import render, redirect, get_object_or_404
from .models import Match, Journey, Player, PlayerMatch
from datetime import date
from .forms import MatchForm, PlayerMatchForm
from django.db.models import Avg
from statistics import mode

# AUTHENTICATION FUNCTIONS
def protected_view(route_function):
    def wrapper_function(request, nickname):
        try:
            Player.objects.get(nickname=nickname)
            return route_function(request, nickname)
        except Player.DoesNotExist:
            return redirect('register')
    return wrapper_function


def register(request):
    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        try:
            player = Player.objects.get(nickname=nickname)
        except Player.DoesNotExist:
            return redirect('register')
        return redirect('default', player.nickname)
    elif request.method == 'GET':
        return render(request, 'login.html')

def sumredirect(request):
    return redirect('register')

class itemDTO:
    def __init__(self, nickname, totalMatches, totalWins, totalSecond, totalKills, totalDamage, effectiveness) -> None:
        self.nickname = nickname
        self.totalMatches = totalMatches
        self.totalWins = totalWins
        self.totalSecond = totalSecond
        self.totalKills = totalKills
        self.totalDamage = totalDamage
        self.effectiveness = effectiveness

@protected_view
def summary(request, nickname):
    personqueryset = Player.objects.all() or []
    dotlist = []
    for person in personqueryset:
        totalMatches = PlayerMatch.objects.filter(player=person).count()
        totalWins = Match.objects.filter(win=person).count()
        totalSecond = Match.objects.filter(second=person).count()
        avgKills = PlayerMatch.objects.filter(player=person).aggregate(Avg('kills')).get('kills__avg')
        avgDamage = PlayerMatch.objects.filter(player=person).aggregate(Avg('damage')).get('damage__avg')

        totalKills = str("{:,.2f}".format(avgKills)) if avgKills else 0
        totalDamage = str("{:,.2f}".format(avgDamage)) if avgDamage else 0
        effectivenessInt = totalWins / totalMatches if totalMatches > 0 else 0
        effectiveness = str("{:,.2f}".format(effectivenessInt))
        dotlist.append(itemDTO(person.nickname, totalMatches, totalWins, totalSecond, totalKills, totalDamage, effectiveness))

    dotlist.sort(key=lambda player: player.effectiveness, reverse=True)
    context = {
        "activeView":"summary",
        "personqueryset": dotlist,
        "nickname": nickname,
        }
    return render(request, 'index.html', context)

@protected_view
def journeys(request, nickname):
    journeyqueryset = Journey.objects.all() or []
    context = {
        "activeView":"journeys",
        "journeyqueryset": journeyqueryset,
        "nickname": nickname,
        }
    return render(request, 'journey.html', context)

def createJourney(request, nickname):
    today = date.today()
    newJourney = Journey(date=today)
    newJourney.save()
    return redirect('journey', nickname, newJourney.id)


class matchDto:
    def __init__(self, id, win, second, players) -> None:
        self.id = id
        self.win = win
        self.second = second
        self.players = players

class matchSumDto:
    def __init__(self, player, winCount, secondCount) -> None:
        self.player = player
        self.winCount = winCount
        self.secondCount = secondCount

def journey(request, nickname, id):
    if request.method == 'GET':
        journey = get_object_or_404(Journey, id=id)
        matches = Match.objects.filter(journey=journey)

        blankForm = MatchForm()
        childForm = PlayerMatchForm()

        matchesDto = []
        winnerMatchesDto = []
        winnerMatches = [x.win for x in matches]
        secondMatches = [x.second for x in matches]
        for match in matches:
            playersList = []
            playerMatches = PlayerMatch.objects.filter(match=match)
            for playerMatch in playerMatches:
                player = get_object_or_404(PlayerMatch, id=playerMatch.id)
                playersList.append(player)
                playersList.sort(key=lambda playerInstance: playerInstance.kills, reverse=True)

                #Count wins through journey
                winCount = winnerMatches.count(player.player)
                secountCount = secondMatches.count(player.player)

                if player.player not in [x.player for x in winnerMatchesDto]:
                    winnerMatchesDto.append(matchSumDto(player=player.player, winCount=winCount, secondCount=secountCount))
            matchesDto.append(matchDto(id=match.id, win=match.win, second=match.second, players=playersList))

        winnerMatchesDto.sort(key=lambda x: x.winCount, reverse=True)
        context = {
            "form": blankForm,
            "childForm": childForm,
            "activeView":"journeys",
            "nickname": nickname,
            "journey": journey,
            "matchesqueryset": matchesDto,
            "journeySum": winnerMatchesDto,
        }
        return render(request, 'journey-detail.html', context)
    elif request.method == 'POST':
        form = request.POST
        # Create Match
        player1 = get_object_or_404(Player, id=form.get('win'))
        player2 = get_object_or_404(Player, id=form.get('second'))
        journey = get_object_or_404(Journey, id=id)
        match = Match(win=player1, second=player2, journey=journey)
        match.save()
        # Create Players
        players = form.getlist('player')
        kills = form.getlist('kills')
        damage = form.getlist('damage')
        for pos in range(len(players)):
            currentPlayer = get_object_or_404(Player, id=players[pos])
            newPlayerMatch = PlayerMatch(
                player=currentPlayer,
                match=match,
                kills=kills[pos],
                damage=damage[pos]
                )
            newPlayerMatch.save()
        return redirect('journey', nickname, id)

def closeJourney(request, nickname, id):
    journey = get_object_or_404(Journey, id=id)
    journey.isActive = False
    journey.save()
    return redirect('journey', nickname, journey.id)