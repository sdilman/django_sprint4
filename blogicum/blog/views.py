from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import CreateView, DeleteView, UpdateView

from .models import Category, Comment, Post
from .forms import CommentForm, PostForm


ITEMS_PER_PAGE = 10


def _get_page_obj(posts, request, items_per_page=ITEMS_PER_PAGE):
    """Make page_obj for page context."""
    return Paginator(posts, items_per_page).get_page(request.GET.get('page'))


def index(request):
    template = 'blog/index.html'
    posts = Post.objects.published().annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    return render(request, template, 
                  context={'page_obj': _get_page_obj(posts, request)})


def post_detail(request, post_id):
    template = 'blog/detail.html'
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    if (
        post.author != user
        and not (post.is_published and post.category.is_published)
    ):
        raise Http404
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = CommentForm()

    context = {
        'form': form,
        'post': post
    }
    return render(request, template, context=context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug
    )
    posts = category.posts.published().annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    page_obj = _get_page_obj(posts, request)
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
    is_owner = request.user == user_profile
    posts = user_profile.posts.annotate(
        comment_count=Count('comments')).order_by('-pub_date')
    if not is_owner:
        posts = posts.published()
    page_obj = _get_page_obj(posts, request)
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


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.object
        return context


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})


class PostUpdateView(PostMixin, OnlyAuthorMixin, UpdateView):

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        return post

    def handle_no_permission(self):
        if self.request.method == 'POST':
            post_id = self.kwargs.get('post_id')
            return redirect('blog:post_detail', post_id=post_id)


class PostDeleteView(PostMixin, OnlyAuthorMixin, DeleteView):

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        return post


class CommentMixinView:
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.object
        return context

    def get_success_url(self):
        return reverse('blog:post_detail', 
                       kwargs={'post_id': self.object.post.id})


class CommentCreateView(CommentMixinView, LoginRequiredMixin, CreateView):

    def form_valid(self, form):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentUpdateView(CommentMixinView, OnlyAuthorMixin, UpdateView):

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id)
        return comment


class CommentDeleteView(CommentMixinView, OnlyAuthorMixin, DeleteView):

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id)
        return comment
