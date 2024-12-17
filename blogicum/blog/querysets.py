from django.db import models
from django.db.models import Count
from django.utils.timezone import now

from .enums import PostFlags


class PostQuerySet(models.QuerySet):

    def selected(
            self,
            flags=(PostFlags.PUBLISHED
                   | PostFlags.RELATED
                   | PostFlags.SORTED
                   | PostFlags.ANNOTATED)
    ):
        """Return published posts."""
        posts = self
        if flags & PostFlags.PUBLISHED:
            posts = self.filter(
                is_published=True,
                pub_date__lte=now(),
                category__is_published=True
            )
        if flags & PostFlags.RELATED:
            posts = posts.select_related('author', 'location', 'category')
        if flags & PostFlags.ANNOTATED:
            posts = posts.annotate(comment_count=Count('comments'))
        if flags & PostFlags.SORTED:
            posts = posts.order_by(*self.model._meta.ordering)
        return posts
