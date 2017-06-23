from django import forms
from .models import Post, Image, Tag, Category
from .widgets import MultiKeyTextInput

class MultiKeyTextField(forms.CharField):
	"""Comma seperated list of keys"""
	# widget=forms.TextInput
	widget = MultiKeyTextInput
	def clean(self, value):
		"""Split string input to a stipped list of strings"""
		if not value:
			return []
		value = value.split(',')
		return list( map( str.strip, value ))	

class PostForm(forms.ModelForm):
	class Meta: 
		model = Post
		fields = ('title', 'text', 'excerpt', 'category','tags')
		widgets = { 'excerpt': forms.Textarea(attrs={'rows':5})}
	tags = MultiKeyTextField()
	

class ImageForm(forms.ModelForm):
	image = forms.ImageField(label='Image')		
	class Meta:
		model = Image
		fields = ('image', 'description')

