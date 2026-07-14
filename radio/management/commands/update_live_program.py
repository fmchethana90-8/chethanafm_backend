from django.core.management.base import BaseCommand
from django.utils import timezone
from radio.models import LiveProgram
from schedule.models import ProgramSchedule


class Command(BaseCommand):
    help = 'Updates live program based on current schedule'

    def handle(self, *args, **kwargs):
        now = timezone.localtime(timezone.now())
        current_time = now.time()

        DAY_MAP = {
            0: 'MON', 1: 'TUE', 2: 'WED',
            3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'
        }
        current_day = DAY_MAP[now.weekday()]

        # Find matching schedule for current time
        current_show = ProgramSchedule.objects.filter(
            day=current_day,
            start_time__lte=current_time,
            end_time__gt=current_time
        ).first()

        live_program, _ = LiveProgram.objects.get_or_create(
            id=1,
            defaults={
                'title': 'Off Air',
                'rj': '',
                'is_live': False,
                'stream_url': 'http://147.93.153.53:8000/live'
            }
        )

        if current_show:
            live_program.title = current_show.title
            live_program.rj = current_show.rj
            live_program.is_live = True
            live_program.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Live: {current_show.title} by {current_show.rj}'
                )
            )
        else:
            live_program.title = 'Off Air'
            live_program.rj = ''
            live_program.is_live = False
            live_program.save()
            self.stdout.write(
                self.style.WARNING('No show now — set to Off Air')
            )