from django.forms import ModelForm
from django import forms
from .models import Match, PlayerMatch

class MatchForm(ModelForm):
    class Meta:
        model = Match
        fields = [
            'win',
            'second',
        ]
        labels = {
            'win': 'Campeon',
            'second': 'Subcampeon',
        }
        widgets = {
            'win': forms.Select(attrs={'class':'form-control'}),
            'second': forms.Select(attrs={'class':'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)

class PlayerMatchForm(ModelForm):
    class Meta:
        model = PlayerMatch
        fields = [
            'player',
            'kills',
            'damage',
        ]
        labels = {
            'player':'Jugador',
            'kills':'Kills',
            'damage':'Daño',
        }
        widgets = {
            'player': forms.Select(attrs={'class':'form-control'}),
            'kills': forms.NumberInput(attrs={'class':'form-control'}),
            'damage': forms.NumberInput(attrs={'class':'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(PlayerMatchForm, self).__init__(*args, **kwargs)

class PlayerMatchMinForm(ModelForm):
    class Meta:
        model = PlayerMatch
        fields = [
            'player',
        ]
        labels = {
            'player':'Jugador',
        }
        widgets = {
            'player': forms.Select(attrs={'class':'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(PlayerMatchForm, self).__init__(*args, **kwargs)