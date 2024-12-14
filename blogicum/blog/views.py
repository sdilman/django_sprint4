from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.http import Http404


from .models import Post, Comment, Category
from .forms import PostForm, CommentForm


NUM_PUBLICATIONS_ON_MAIN_PAGE = 10
NUM_ITEMS_PER_PAGE = 10


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
    user = request.user
    post = get_object_or_404(Post, id=id)
    if post.author != user and not post.is_published:
        raise Http404

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('blog:post_detail', id=post.id)
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
    is_owner = request.user == user_profile
    if is_owner:
        post_list = user_profile.posts.all()
    else:
        post_list = user_profile.posts.published()
    page_obj = _get_page_obj(post_list, request)

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
        return reverse('blog:post_detail', kwargs={'id': self.object.id})

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        return post

    def handle_no_permission(self):
        if self.request.method == 'POST':
            post_id = self.kwargs.get('post_id')
            return redirect('blog:post_detail', id=post_id)


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
        return reverse('blog:post_detail', kwargs={'id': self.object.post.id})


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
