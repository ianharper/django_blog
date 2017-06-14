from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Post, Image, Tag, Category

class MultiKeyTextField(forms.CharField):
	"""Comma seperated list of keys"""
	def clean(self, value):
		"""Split string input to a stipped list of strings"""
		if not value:
			return []
		value = value.split(',')
		return list( map( str.strip, value ))		

class PostForm(forms.ModelForm):
	class Meta: 
		model = Post
		fields = ('title', 'text', 'category')
	tags = MultiKeyTextField()

	# def save(self, commit=True):
	# 	form = super(PostForm, self).save(commit=False)
	# 	form.save()
	# 	import pdb; pdb.set_trace()
	# 	for tagName in form.tags:
	# 		tag = Tag.objects.filter(name=tagName)
	# 		if not(tag):
	# 			Tag.objects.create(name=tagName)
	# 		if not( tag in form.tags.all() ):
	# 			post.tags.add(tag)
	# 	return form

class ImageForm(forms.ModelForm):
	image = forms.ImageField(label='Image')		
	class Meta:
		model = Image
		fields = ('image', 'description')

