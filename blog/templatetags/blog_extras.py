from django import template
import markdown

register = template.Library()

@register.filter
def markdownify(text):
	"""Convert markdown text to HTML"""
	# import pdb; pdb.set_trace()
	return markdown.markdown(text, safe_mode='escape')

@register.filter
def imageCaptions(text, img_pos=None):
	# import pdb; pdb.set_trace()
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
