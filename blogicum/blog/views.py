from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm

from .models import Post, Category


NUM_PUBLICATIONS_ON_MAIN_PAGE = 5


def index(request):
    template = 'blog/index.html'
    post_list = Post.objects.related().published().filter(
        category__is_published=True
    )[:NUM_PUBLICATIONS_ON_MAIN_PAGE]
    context = {'post_list': post_list}
    return render(request, template, context=context)


def post_detail(request, id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post.objects.related().published(),
        pk=id,
        category__is_published=True
    )
    context = {'post': post}
    return render(request, template, context=context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug
    )
    post_list = category.posts.published()
    template = 'blog/category.html'
    context = {
        'category': category,
        'post_list': post_list
    }
    return render(request, template, context=context)


def profile_view(request, username):
    template = 'blog/profile.html'
    user_profile = get_object_or_404(User, username=username)
    is_owner = request.user == user_profile
    context = {
        'profile': user_profile,
        'page_obj': user_profile.posts.published(),
        'is_owner': is_owner
    }
    return render(request, template, context=context)


@login_required
def profile_edit_view(request):
    template = 'blog/profile_edit.html'
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, template, context={'form': form})


def create_post(request):
    ...