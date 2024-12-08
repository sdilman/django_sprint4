from django.db import models
from django.utils.timezone import now


class PostQuerySet(models.QuerySet):

    def related(self):
        """Add related models."""
        return self.select_related('author', 'location', 'category')

    def published(self):
        """Return published posts."""
        return self.filter(
            is_published=True,
            pub_date__lte=now(),
        )
