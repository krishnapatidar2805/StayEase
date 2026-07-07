from django import forms
from rooms.models import Room, RoomCategory, Amenity


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'category', 'description', 'price_per_night', 'capacity', 'beds',
                  'size_sqft', 'amenities', 'best_for', 'thumbnail', 'is_available', 'total_units', 'rating']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price_per_night': forms.NumberInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'beds': forms.NumberInput(attrs={'class': 'form-control'}),
            'size_sqft': forms.NumberInput(attrs={'class': 'form-control'}),
            'amenities': forms.CheckboxSelectMultiple(),
            'best_for': forms.Select(attrs={'class': 'form-select'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'total_units': forms.NumberInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }
