from django.db import models

DAYS = [
    ('MON','Monday'),('TUE','Tuesday'),('WED','Wednesday'),
    ('THU','Thursday'),('FRI','Friday'),('SAT','Saturday'),('SUN','Sunday'),
]

class ProgramSchedule(models.Model):
    day = models.CharField(max_length=3, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    title = models.CharField(max_length=100)
    rj = models.CharField(max_length=100)

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.day} {self.title}"