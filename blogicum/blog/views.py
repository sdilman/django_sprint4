from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator


from .models import Post, Category
from .forms import PostForm


NUM_PUBLICATIONS_ON_MAIN_PAGE = 5
NUM_ITEMS_PER_PAGE = 2


def _get_page_obj(post_list, request):
    """Make page_obj for page context."""
    paginator = Paginator(post_list, NUM_ITEMS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    template = 'blog/index.html'
    post_list = Post.objects.related().published().filter(
        category__is_published=True
    )[:NUM_PUBLICATIONS_ON_MAIN_PAGE]
    page_obj = _get_page_obj(post_list, request)
    context = {'page_obj': page_obj}
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
    page_obj = _get_page_obj(post_list, request)
    template = 'blog/category.html'
    context = {
        'category': category,
        'page_obj': page_obj
    }
    print(context)
    return render(request, template, context=context)


def profile_view(request, username):
    template = 'blog/profile.html'
    user_profile = get_object_or_404(User, username=username)
    post_list = user_profile.posts.published()
    page_obj = _get_page_obj(post_list, request)
    is_owner = request.user == user_profile
    context = {
        'profile': user_profile,
        'page_obj': page_obj,
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


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})
