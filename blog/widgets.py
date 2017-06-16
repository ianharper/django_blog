from django.forms import widgets

class MultiKeyTextInput(widgets.Input):
	"""docstring for MultiKeyTextInput"""

	def render(self, name, value, attrs=None, **kwargs):
		tagMap = map(lambda tag: tag.name, value)
		tagNames = ', '.join( list(tagMap) )
		return super(MultiKeyTextInput, self).render(name, tagNames)