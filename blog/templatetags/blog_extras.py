from django import template
from django.utils.html import format_html
from django.urls import reverse
from blog.models import *
import markdown

register = template.Library()

@register.filter
def markdownify(text):
	"""Convert markdown text to HTML"""
	return markdown.markdown(text, safe_mode='escape')


@register.filter
def imageCaptions(text, img_pos=None):
	if not(img_pos): img_pos = text.find('<img')
	if img_pos > -1:
		img_end = text.find('>', img_pos)
		print(text[img_pos:img_end+1])
		img_alt = ''
		img_alt_pos = text.find('alt=', img_pos, img_end)
		if img_alt_pos > -1: 
			img_alt_end = text.find('"', img_alt_pos + 5)
			img_alt = '<p class="caption text-center">' + text[img_alt_pos + 5:img_alt_end] + '</p>'
		text  = text[:img_pos] + '<div class="thumbnail col-md-offset-3 center-thumbnail">' + text[img_pos:img_end+1] + img_alt + '</div>' + text[img_end+1:]
		img_pos = text.find('<img', img_end)
		if img_pos > -1: text = imageCaptions(text, img_pos)
	return text


@register.simple_tag
def categoryTagList(categoryName):
	tagListHtml = []
	tagList = Category.objects.filter(name=categoryName)[0].getCategoryTags()
	if len(tagList) > 0:
		categorySubMenu = categoryName.replace(' ', '') + 'Menu'
		tagListHtml.append('<a href="#' + categorySubMenu + '" data-toggle="collapse" aria-expanded="false"></a>')
		tagListHtml.append('<ul class="collapse list-unstyled sub-menu" id="' + categorySubMenu + '">')
		for tag in tagList:
			tagListHtml.append('<li><a href="' + 
				reverse('tag_list', args=[tag.name.replace(' ', '_')]) + 
				'">' + tag.name.title() + '</a></li>')
		tagListHtml.append('</ul>')
	return format_html( '\n'.join(tagListHtml) ) 
