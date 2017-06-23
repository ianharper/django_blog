from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.shortcuts import redirect
from django import forms
from django.forms import modelformset_factory
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage
from django.http import HttpResponse, HttpResponseNotFound
from .models import Post, Image, Tag
from .forms import PostForm, ImageForm
import re

# import pdb; pdb.set_trace()

def post_list(request, page):
	if not(page): page = 1
	post_query = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
	posts = Paginator(post_query, 10)   
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
		formset = ImageFormSet(request.POST, request.FILES, 
			queryset=Image.objects.none())
		if save_post(request, form, formset):
	 		return redirect('post_detail', pk=post.pk)
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
	text = post.text.split('\r\n')
	image_pattern = re.compile('(\!\[[A-Za-z\s0-9]*?\])(\(.*?\))')

	images = []
	for image in post.image_set.all():
		images.append(image)

	for line in range(len(text)):
		if images: 
			url = images[0].image.url
			description = images[0].description
		else:
			break
		line_text = text[line]
		text[line] = image_pattern.sub(r'\1('+url+' "'+description+'")', text[line])
		if text[line] != line_text:
			images.pop(0)
	# import pdb; pdb.set_trace()
	post.text = '\r\n'.join(text)
	return images

def category_list(request, name, page=1):
	if not(page): page = 1
	post_query = Post.objects.filter(
		published_date__lte=timezone.now(),
		category__name__contains=name
		).order_by('-published_date')
	posts = Paginator(post_query, 10)
	try:
		return render(request, 'blog/category_list.html', {'posts': posts.page(page)})
	except InvalidPage:
		return HttpResponseNotFound('<h1>Page not found</h1>')

def tag_list(request, name, page=1):
	if not(page): page = 1
	post_query = Post.objects.filter(
		published_date__lte=timezone.now(),
		tags__name__contains=name
		).order_by('-published_date')
	posts = Paginator(post_query, 10)
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

		for form in formset:
			if not 'image' in form: continue
			image = form['image']
			description = form['description']
			photo = Image(post = post, image = image, description = description)
			photo.save()
		return True
	else:
		return False