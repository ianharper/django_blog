from django.forms import widgets
from .models import Tag

class MultiKeyTextInput(widgets.Input):
	"""docstring for MultiKeyTextInput"""

	def render(self, name, value, attrs=None, **kwargs):
		if value == None: value = Tag.objects.none()
		tagMap = map(lambda tag: tag.name, value)
		tagNames = ', '.join( list(tagMap) )
		return super(MultiKeyTextInput, self).render(name, tagNames)