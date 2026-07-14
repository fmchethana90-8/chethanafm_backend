from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def update_live_program():
    """
    Runs every minute.
    Checks current time against schedule and updates LiveProgram.
    """
    try:
        from .models import LiveProgram
        from schedule.models import ProgramSchedule

        now = timezone.localtime(timezone.now())
        current_day = now.strftime('%a').upper()[:3]
        current_time = now.time()

        # Day mapping
        DAY_MAP = {
            'MON': 'MON', 'TUE': 'TUE', 'WED': 'WED',
            'THU': 'THU', 'FRI': 'FRI', 'SAT': 'SAT', 'SUN': 'SUN'
        }
        day = DAY_MAP.get(current_day, current_day)

        # Find matching schedule
        current_show = ProgramSchedule.objects.filter(
            day=day,
            start_time__lte=current_time,
            end_time__gt=current_time
        ).first()

        # Get or create the live program entry
        live_program, created = LiveProgram.objects.get_or_create(
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
            logger.info(f"Live: {current_show.title} by {current_show.rj}")
        else:
            live_program.title = 'Off Air'
            live_program.rj = ''
            live_program.is_live = False
            live_program.save()
            logger.info("No show scheduled now — set to Off Air")

    except Exception as e:
        logger.error(f"Scheduler error: {e}")


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_live_program,
        'interval',
        minutes=1,
        id='update_live_program',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started.")