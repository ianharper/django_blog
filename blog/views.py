from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from django import forms
from django.forms import modelformset_factory
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage
from django.http import HttpResponse, HttpResponseNotFound
from .models import Post, Image, Tag
from .forms import PostForm, ImageForm
import re


def post_list(request, page):
	if not(page): page = 1
	post_query = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
	posts = Paginator(post_query, 5)
	try:
		return render(request, 'blog/post_list.html', {'posts': posts.page(page)})
	except InvalidPage:
		return HttpResponseNotFound('<h1>Page not found</h1>')

def post_detail(request, pk):
	post = get_object_or_404(Post, pk=pk)
	images = swap_image_index_for_url(post)
	return render(request, 'blog/post_detail.html', {'post': post, 'images': images})

def post_new(request):
	ImageFormSet = modelformset_factory(Image, form = ImageForm, extra = 3)

	if request.method == "POST":
		form = PostForm(request.POST)
		formset = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.none())
		if save_post(request, form, formset):
			# todo: fix this kluge. It was needed because a refactor took the pk and burried it in the save_post function.
			post_key = Post.objects.filter(title=form.cleaned_data['title'])[0].pk
			return redirect('post_detail', pk=post_key)
		else:
			print(form.errors, formset.errors)
	else:
		form = PostForm()
		formset = ImageFormSet(queryset = Image.objects.none())
	return render(request, 'blog/post_edit.html', {'form': form, 'formset': formset})

			

def post_edit(request, pk):
	post = get_object_or_404(Post, pk=pk)
	# images = post.image_set.all()
	ImageFormSet = modelformset_factory(Image, form = ImageForm, extra = 3)

	if request.method == "POST":
		form = PostForm(request.POST, instance=post)
		formset = ImageFormSet(request.POST, request.FILES, queryset=post.image_set.all())
		if save_post(request, form, formset):
	 		return redirect('post_detail', pk=post.pk)
	else:
		form = PostForm(instance=post)
		formset = ImageFormSet(queryset = post.image_set.all())
	return render(request, 'blog/post_edit.html', {'form': form, 'formset': formset})

def swap_image_index_for_url(post):
	text = post.text.split('\n')
	image_pattern = re.compile('(\!\[.*?\]\[(.*?)\])(\]\(.*?\))?')

	images = []
	for image in post.image_set.all():
		images.append(image)
	
	for line in range(len(text)):
		line_text = text[line]
		pattern_match = image_pattern.search(line_text)
		if pattern_match != None:
			image = images[int(pattern_match.group(2)) - 1]

			if image.thumb_width == '': image.thumb_width = '400'
			size_string = image.thumb_width + 'x' + image.thumb_width
			thumb = image.image.thumbnail[size_string]
			thumb_url = thumb.url

			image_reference = '[' + pattern_match.group(2) + ']: ' + thumb_url #image.image.url
			text.append('\r\n' + image_reference)
			images[int(pattern_match.group(2)) - 1] = None
			if not(pattern_match.group(3)):
				text[line] = image_pattern.sub(r'[\1]('+image.image.url+')', line_text)
			
	post.text = '\r\n'.join(text)
	for i in range(len(images)-1, -1, -1):
		if images[i] == None: del images[i]
	return images

def category_list(request, name, page=1):
	if not(page): page = 1
	post_query = Post.objects.filter(
		published_date__lte=timezone.now(),
		category__name__contains=name
		).order_by('-published_date')
	posts = Paginator(post_query, 5)
	for post in range(len(post_query)):
		swap_image_index_for_url(post_query[post])
	try:
		return render(request, 'blog/category_list.html', {'posts': posts.page(page)})
	except InvalidPage:
		return HttpResponseNotFound('<h1>Page not found</h1>')

def tag_list(request, name, page=1):
	if not(page): page = 1
	name = name.replace("_", " ")
	post_query = Post.objects.filter(
		published_date__lte=timezone.now(),
		tags__name__contains=name
		).order_by('-published_date')
	for post in range(len(post_query)):
		swap_image_index_for_url(post_query[post])
	posts = Paginator(post_query, 5)
	try:
		return render(request, 'blog/tag_list.html', {'posts': posts.page(page)})
	except InvalidPage:
		return HttpResponseNotFound('<h1>Page not found</h1>')

def save_post(request, form, formset):
	if form.is_valid():
		post = form.save(commit=False)
		post.author = request.user
		post.published_date = timezone.now()
		if not(post.excerpt): 
			if len(post.text) > 500: 
				post.excerpt = post.text[:497] + '...'
			else:
				post.excerpt = post.text[:500]
		post.save()
		
		for tagName in form.cleaned_data['tags']:
			try:
				tag = Tag.objects.get(name=tagName)
			except Tag.DoesNotExist:
				tag = Tag.objects.create(name=tagName)
			if not( tag in post.tags.all() ):
				post.tags.add(tag)

		# Remove tags from post 
		for tag in post.tags.all():
			if not(tag.name in form.cleaned_data['tags']):
				post.tags.remove(tag)

		for image_form in formset.cleaned_data:
			if not 'image' in image_form: continue
			photo = Image()
			if image_form['id']: photo = Image.objects.filter(pk=image_form['id'].pk)
			photo.image = image_form['image'][0]
			photo.description = image_form['description']
			photo.post = post
			photo.save()
		return True
	else:
		return False