from django.shortcuts import render, redirect, get_object_or_404
from .models import Match, Journey, Player, PlayerMatch
from datetime import date
from .forms import MatchForm, PlayerMatchForm
from django.db.models import Avg
from statistics import mode
from itertools import combinations
import random

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
    journeyqueryset = Journey.objects.filter(JourneyType="Journey").order_by('-number') or []
    context = {
        "activeView":"journeys",
        "journeyqueryset": journeyqueryset,
        "nickname": nickname,
        }
    return render(request, 'journey.html', context)

def createJourney(request, nickname):
    journeyCount = Journey.objects.count() + 1
    today = date.today()
    newJourney = Journey(date=today, number=journeyCount)
    newJourney.save()
    return redirect('journey', nickname, newJourney.id)


class matchDto:
    def __init__(self, id, win, second, players, number=0, wasPlayed=True, shouldShow=True) -> None:
        self.id = id
        self.win = win
        self.second = second
        self.players = players
        self.number = number
        self.wasPlayed = wasPlayed
        self.shouldShow = shouldShow


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
                playersList.append(playerMatch)
                playersList.sort(key=lambda playerInstance: 0 if playerInstance.kills is None else playerInstance.kills, reverse=True)

                #Count wins through journey
                winCount = winnerMatches.count(playerMatch.player)
                secountCount = secondMatches.count(playerMatch.player)

                if playerMatch.player not in [x.player for x in winnerMatchesDto]:
                    winnerMatchesDto.append(matchSumDto(player=playerMatch.player, winCount=winCount, secondCount=secountCount))
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

def tournamentList(request, nickname):
    if request.method == 'GET':
        tournamentqueryset = Journey.objects.filter(JourneyType="Tournament").order_by('-number') or []
        childForm = PlayerMatchForm()
        context = {
            "childForm": childForm,
            "activeView":"tournament",
            "journeyqueryset": tournamentqueryset,
            "nickname": nickname,
            }
        return render(request, 'tournaments.html', context)
    elif request.method == 'POST':
        #Create Journey
        journeyCount = Journey.objects.filter(JourneyType="Tournament").count() + 1
        today = date.today()
        newJourney = Journey(date=today, number=journeyCount, isActive=True, JourneyType="Tournament")
        newJourney.save()

        # Create Players
        form = request.POST
        playerNames = form.getlist('player')
        players = []
        for pos in range(len(playerNames)):
            currentPlayer = get_object_or_404(Player, id=playerNames[pos])
            if(currentPlayer):
                players.append(currentPlayer)

        #Create Matches to be played
        matchesToPlay = list(combinations(players, 2))
        random.shuffle(matchesToPlay)
        for pos in range(len(matchesToPlay)):
            match = Match(number=pos+1, journey=newJourney, wasPlayed=False)
            match.save()
            player1 = PlayerMatch(
                player=matchesToPlay[pos][0],
                match=match,
                )
            player1.save()
            player2 = PlayerMatch(
                player=matchesToPlay[pos][1],
                match=match,
                )
            player2.save()
        
        return redirect('tournament', nickname, newJourney.id)
    
def tournament(request, nickname, id):
    journey = get_object_or_404(Journey, id=id)
    if request.method == 'GET':
        matches = Match.objects.filter(journey=journey)

        matchesDto = []
        winnerMatchesDto = []
        winnerMatches = [x.win for x in matches]
        secondMatches = [x.second for x in matches]
        for match in matches:
                    playersList = []
                    playerMatches = PlayerMatch.objects.filter(match=match)
                    for playerMatch in playerMatches:
                        playersList.append(playerMatch)

                        #Count wins through journey
                        winCount = winnerMatches.count(playerMatch.player) * 3
                        secountCount = secondMatches.count(playerMatch.player)

                        if playerMatch.player not in [x.player for x in winnerMatchesDto]:
                            winnerMatchesDto.append(matchSumDto(player=playerMatch.player, winCount=winCount, secondCount=secountCount))
                    matchesDto.append(matchDto(id=match.id, win=match.win, second=match.second, players=playersList, number=match.number, wasPlayed=match.wasPlayed, shouldShow=journey.Round == match.journeyRound))

        winnerMatchesDto.sort(key=lambda x: x.winCount, reverse=True)
        playedMatches = Match.objects.filter(journey=journey, wasPlayed=True).count()
        roundFinished = playedMatches == len(matchesDto)
        context = {
            "journey": journey,
            "activeView":"tournament",
            "nickname": nickname,
            "matchesqueryset": matchesDto,
            "journeySum": winnerMatchesDto,
            "matchesToDisplay" : playedMatches + 1,
            "roundFinished": roundFinished,
            "currentRound": journey.Round,
        }
        return render(request, 'tournament-detail.html', context)
    elif request.method == 'POST':
        items = [value for  value in request.POST.items()]
        for matchPlayed in items[1:]:
            matchNumber = matchPlayed[0]
            winnerValue = matchPlayed[1]
            currentMatch = Match.objects.filter(journey=journey, number=matchNumber).first()
            playerMatches = PlayerMatch.objects.filter(match=currentMatch)
            playersList = []

            for playerMatch in playerMatches:
                playersList.append(playerMatch)
            
            winner = [element for element in playersList if element.player.nickname == winnerValue]
            looser = [element for element in playersList if element not in winner]
            currentMatch.win = winner[0].player
            currentMatch.second = looser[0].player
            currentMatch.wasPlayed = True

            currentMatch.save()
        return redirect('tournament', nickname, id)
    
def closeTournament(request, nickname, id):
    journey = get_object_or_404(Journey, id=id)
    journey.isActive = False
    journey.save()
    return redirect('tournament', nickname, journey.id)

def nextRount(request, nickname, id, matchesDisplayed):
    journey = get_object_or_404(Journey, id=id)
    journey.Round = journey.Round + 1
    journey.save()

    # Get players for next round
    matches = Match.objects.filter(journey=journey)
    players = []
    for match in matches:
        playerMatches = PlayerMatch.objects.filter(match = match)
        players.extend([player.player for player in playerMatches])

    players = set(players)
    matchesToPlay = list(combinations(players, 2))
    random.shuffle(matchesToPlay)

    matchNumber = int(matchesDisplayed)
    for pos in range(len(matchesToPlay)):
        match = Match(number=matchNumber, journey=journey, journeyRound=journey.Round, wasPlayed=False)
        match.save()
        player1 = PlayerMatch(
            player=matchesToPlay[pos][0],
            match=match,
            )
        player1.save()
        player2 = PlayerMatch(
            player=matchesToPlay[pos][1],
            match=match,
            )
        player2.save()
        matchNumber = matchNumber + 1

    return redirect('tournament', nickname, id)