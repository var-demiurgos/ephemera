from django import forms
from .models import Ephemera

class EditMyListForm(forms.ModelForm):

	class Meta:
		model = Ephemera
		fields = ('url', 'message')
		labels = {
			'url' : "URL",
			'message' : 'メモ',
		}

	url = forms.URLField(disabled=True)