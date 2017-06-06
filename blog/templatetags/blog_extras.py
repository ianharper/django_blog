from django import template
import markdown

register = template.Library()

@register.filter
def markdownify(text):
	"""Convert markdown text to HTML"""
	return markdown.markdown(text, safe_mode='escape')
