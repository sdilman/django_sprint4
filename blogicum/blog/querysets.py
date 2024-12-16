from django.db import models
from django.utils.timezone import now


class PostQuerySet(models.QuerySet):

    def published(self, related=True):
        """Return published posts."""
        posts = self.filter(
            is_published=True,
            pub_date__lte=now(),
            category__is_published=True
        )
        if related:
            posts = posts.select_related('author', 'location', 'category')
        return posts
