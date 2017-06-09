from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.shortcuts import redirect
from django import forms
from django.forms import modelformset_factory
from django.template import RequestContext
from .models import Post, Image
from .forms import PostForm, ImageForm
import re

def post_list(request):
	posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
	return render(request, 'blog/post_list.html', {'posts': posts})

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
		if form.is_valid() and formset.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			post.published_date = timezone.now()
			post.save()

			for form in formset:
				if not 'image' in form.cleaned_data: continue
				image = form.cleaned_data['image']
				description = form.cleaned_data['description']
				photo = Image(post = post, image = image, description = description)
				photo.save()
			return redirect('post_detail', pk=post.pk)
		else:
			print(post.errors, formset.errors)
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
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			post.published_date = timezone.now()
			post.save()
			
			for form in formset:
				if not 'image' in form: continue
				image = form['image']
				description = form['description']
				photo = Image(post = post, image = image, description = description)
				photo.save()
			return redirect('post_detail', pk=post.pk)
		else:
			print(post.errors, formset.errors)
	else:
		form = PostForm(instance=post)
		formset = ImageFormSet(queryset = post.image_set.all())
		# import pdb; pdb.set_trace()
	return render(request, 'blog/post_edit.html', {'form': form, 'formset': formset})

def swap_image_index_for_url(post):
	text = post.text.split('\r\n')
	image_pattern = re.compile('(\!\[[A-Za-z\s0-9]*?\])(\(.*?\))')

	images = []
	for image in post.image_set.all():
		images.append(image)

	for line in range(len(text)):
		# matches = image_pattern.findall(text[line])
		# for match in matches:
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