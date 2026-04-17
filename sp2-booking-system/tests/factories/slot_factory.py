from datetime import timedelta
from tests.human.unit.conftest import NOW

from models import Slot, SlotStatus


def create_slot(slot_id=1, specialist_id=10, hours_from_now=48):
    start = NOW + timedelta(hours=hours_from_now)
    end = start + timedelta(minutes=30)

    return Slot(
        id=slot_id,
        specialist_id=specialist_id,
        start_time=start,
        end_time=end,
        status=SlotStatus.AVAILABLE,
    )
