from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify

class Category(models.Model):
	"""	Post Category"""
	name = models.CharField(max_length=100)	
	tagline = models.CharField(max_length=200, default = '', blank = True)

	def __str__(self):
		return self.name

class Post(models.Model):
	author = models.ForeignKey('auth.User')
	title = models.CharField(max_length=200)
	text = models.TextField()
	created_date = models.DateTimeField(
		default = timezone.now)
	published_date = models.DateTimeField(
		blank = True, null = True)
	category = models.ForeignKey(Category, default = '', blank = True, null = True)

	def publish(self):
		self.published_date = timezone.now()
		self.save

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
	image = models.ImageField(upload_to = get_image_filename, verbose_name = 'Image')
	# uploaded_at = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return self.description

