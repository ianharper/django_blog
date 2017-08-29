from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from versatileimagefield.fields import VersatileImageField

class Category(models.Model):
	"""	Post Category"""
	name = models.CharField(max_length=100)	
	tagline = models.CharField(max_length=200, default = '', blank = True)

	def __str__(self):
		return self.name

class Tag(models.Model):
	"""Post Tag"""
	name = models.CharField('Tags', max_length=100)

	def __str__(self):
		return self.name 

class Post(models.Model):
	author = models.ForeignKey('auth.User')
	title = models.CharField(max_length=200)
	text = models.TextField()
	created_date = models.DateTimeField(default = timezone.now)
	published_date = models.DateTimeField(blank = True, null = True)
	category = models.ForeignKey(Category, default = '', blank = True, null = True)
	tags = models.ManyToManyField(Tag, default='', blank=True)
	excerpt = models.CharField(max_length=500, blank=True, default='')

	def getTagNames(self):
		tagNames = ''
		for tag in self.tags.all():
			if tagNames: tagNames += ', '
			tagNames += tag.name
		return tagNames

	def getTagLi(self):
		tagLi = ''
		for tag in self.tags.all():
			tagLi += '<a href="{% url \'tag_list\' name='+tag.name+' %}">'
			tagLi += tag.name
			tagLi += '</a>'
		return tagLi

	def publish(self):
		self.published_date = timezone.now()
		self.save

	def create(item):
		from django.contrib.auth.models import User
		author = User.objects.filter(pk=1)[0]
		category = Category.objects.filter(pk=item['category'])[0]
		post = Post.objects.create(title=item['title'], category=category, 
			text=item['text'], author=author, published_date=item['published_date'], 
			created_date=item['published_date'])
		for tagName in item['tags']:
			post.tags.add(Tag.objects.filter(name=tagName))
		post.save()
		return post


	def __str__(self):
		return self.title

def get_image_filename(instance, filename):
	title = instance.post.title
	slug = slugify(title)
	return "images/%s-%s" % (slug, filename)

class Image(models.Model):
	"""Uploaded Images"""
	description = models.CharField(max_length = 255, blank = True)		
	post = models.ForeignKey(Post, default = None)
	# image = models.ImageField(upload_to = get_image_filename, verbose_name = 'Image')
	image = VersatileImageField(upload_to = get_image_filename, verbose_name = 'Image')
	thumb_width = models.CharField(max_length = 4, blank = True)

	def __str__(self):
		return self.description

	def thumb_crop(self):
		return self.image.crop['230x175'].url
