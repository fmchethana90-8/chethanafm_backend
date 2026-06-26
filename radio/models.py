from django.db import models


class LiveProgram(models.Model):

    title = models.CharField(max_length=100)
    rj = models.CharField(max_length=100)
    is_live = models.BooleanField(default=False)
    stream_url = models.URLField(default="https://radio.chethanafm.com/live")

    def save(self, *args, **kwargs):
        if self.is_live:
            LiveProgram.objects.exclude(pk=self.pk).update(is_live=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title