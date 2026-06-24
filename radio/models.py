from django.db import models

# Create your models here.

class LiveProgram(models.Model):

    title = models.CharField(max_length=100)
    rj= models.CharField(max_length=100)
    is_live=models.BooleanField(default=False)
    stream_url=models.URLField(default="https://radio.chethanafm.com/live")

    def __str__(self):

        return self.title