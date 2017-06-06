from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.shortcuts import redirect
from django import forms
from django.forms import modelformset_factory
from django.template import RequestContext
from .models import Post, Image
from .forms import PostForm, ImageForm

def post_list(request):
	posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
	return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
	post = get_object_or_404(Post, pk=pk)
	images = post.image_set.all()
	# import pdb; pdb.set_trace()
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
	if request.method == "POST":
		form = PostForm(request.POST, instance=post)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = requestuser
			post.published_date = timezone.now()
			post.save()
			return redirect('post_detail', pk=post.pk)
	else:
		form = PostForm(instance=post)
	return render(request, 'blog/post_edit.html', {'form': form})