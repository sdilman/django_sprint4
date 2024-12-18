from django.db import models
from django.db.models import Count
from django.utils.timezone import now


class PostQuerySet(models.QuerySet):

    def selected(
        self,
        apply_published=True,
        apply_related=True,
        apply_annotated=True
    ):
        """Return selected posts."""
        posts = self
        if apply_published:
            posts = self.filter(
                is_published=True,
                pub_date__lte=now(),
                category__is_published=True
            )
        if apply_related:
            posts = posts.select_related('author', 'location', 'category')
        if apply_annotated:
            posts = posts.annotate(
                comment_count=Count('comments')
            ).order_by(
                *self.model._meta.ordering
            )
        return posts
