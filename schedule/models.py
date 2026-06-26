from django.db import models
from rest_framework import serializers

DAYS = [
    ('MON', 'Monday'),
    ('TUE', 'Tuesday'),
    ('WED', 'Wednesday'),
    ('THU', 'Thursday'),
    ('FRI', 'Friday'),
    ('SAT', 'Saturday'),
    ('SUN', 'Sunday'),
]

DAY_ORDER = {
    'MON': 1,
    'TUE': 2,
    'WED': 3,
    'THU': 4,
    'FRI': 5,
    'SAT': 6,
    'SUN': 7,
}


class ProgramSchedule(models.Model):
    day = models.CharField(max_length=3, choices=DAYS)
    day_order = models.PositiveSmallIntegerField(default=1, editable=False)
    start_time = models.TimeField()
    end_time = models.TimeField()
    title = models.CharField(max_length=100)
    rj = models.CharField(max_length=100)

    class Meta:
        ordering = ['day_order', 'start_time']

    def save(self, *args, **kwargs):
        # Automatically set day_order based on the selected day
        self.day_order = DAY_ORDER.get(self.day, 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.day} {self.title}"
    
    def validate(self, data):
        overlapping = ProgramSchedule.objects.filter(
            day=data['day'],
            start_time__lt=data['end_time'],
            end_time__gt=data['start_time'],
        )
        if self.instance:
            overlapping = overlapping.exclude(pk=self.instance.pk)
        if overlapping.exists():
            raise serializers.ValidationError("This time slot overlaps with an existing program.")
        return data