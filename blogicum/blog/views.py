from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post


ITEMS_PER_PAGE = 10


def get_page_obj(posts, request, items_per_page=ITEMS_PER_PAGE):
    """Make page_obj for page context."""
    return Paginator(posts, items_per_page).get_page(request.GET.get('page'))


def index(request):
    return render(
        request,
        'blog/index.html',
        context={
            'page_obj': get_page_obj(
                Post.objects.selected(),
                request
            )
        }
    )


def post_detail(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    if post.author != user:
        post = get_object_or_404(
            Post.objects.selected(apply_related=False, apply_annotated=False),
            id=post_id
        )
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        return redirect('blog:post_detail', post.id)
    return render(request, 'blog/detail.html',
                  context={'form': form, 'post': post})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug
    )
    return render(
        request, 'blog/category.html',
        context={
            'category': category,
            'page_obj': get_page_obj(
                category.posts.selected(),
                request
            )
        }
    )


def profile_view(request, username):
    author = get_object_or_404(User, username=username)
    return render(
        request, 'blog/profile.html',
        context={
            'profile': author,
            'page_obj': get_page_obj(
                author.posts.selected(
                    apply_published=(request.user != author)
                ),
                request
            )
        }
    )


@login_required
def profile_edit_view(request):
    template = 'blog/profile_edit.html'
    form = UserChangeForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', request.user.username)
    return render(request, template, context={'form': form})


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, post=self.object)


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostUpdateView(PostMixin, OnlyAuthorMixin, UpdateView):

    def get_success_url(self):
        return reverse('blog:post_detail',
                       args=[self.kwargs[self.pk_url_kwarg]])

    def handle_no_permission(self):
        if self.request.method == 'POST':
            return redirect('blog:post_detail', self.kwargs[self.pk_url_kwarg])
        else:
            raise Http404(
                f'Обращаться к странице {self.request.path} используя'
                f' метод {self.request.method} не разрешается.'
            )


class PostDeleteView(PostMixin, OnlyAuthorMixin, DeleteView):

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class CommentMixinView:
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, comment=self.object)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['post_id']])


class CommentCreateView(CommentMixinView, LoginRequiredMixin, CreateView):

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentUpdateView(CommentMixinView, OnlyAuthorMixin, UpdateView):
    ...


class CommentDeleteView(CommentMixinView, OnlyAuthorMixin, DeleteView):
    ...
