import pytest
from freezegun import freeze_time

from services import BookingError
from tests.human.unit.conftest import NOW
from tests.factories.slot_factory import create_slot


BOOKING_LIMIT = 3


class TestBooking:

    @freeze_time(NOW)
    def test_successful_booking(self, service, repo):
        slot = create_slot()
        repo.add_slot(slot)

        booking = service.book_slot(user_id=1, slot_id=1)

        assert booking.user_id == 1
        assert booking.slot_id == 1
        assert repo.get_slot(1).status.name == "BOOKED"

    @freeze_time(NOW)
    def test_booking_nonexistent_slot_raises(self, service):
        with pytest.raises(BookingError, match="Slot does not exist"):
            service.book_slot(user_id=1, slot_id=999)

    @freeze_time(NOW)
    def test_double_booking_prevented(self, service, repo):
        slot = create_slot()
        repo.add_slot(slot)

        service.book_slot(user_id=1, slot_id=1)

        with pytest.raises(BookingError, match="Slot is not available"):
            service.book_slot(user_id=2, slot_id=1)

    @freeze_time(NOW)
    def test_booking_limit_enforced(self, service, repo):
        for i in range(1, BOOKING_LIMIT + 2):
            repo.add_slot(create_slot(slot_id=i, hours_from_now=48 + i))

        for i in range(1, BOOKING_LIMIT + 1):
            service.book_slot(user_id=1, slot_id=i)

        with pytest.raises(BookingError, match="booking limit"):
            service.book_slot(user_id=1, slot_id=BOOKING_LIMIT + 1)

    @freeze_time(NOW)
    @pytest.mark.parametrize("slot_id", [1, 2, 3])
    def test_user_can_book_up_to_limit(self, service, repo, slot_id):
        repo.add_slot(create_slot(slot_id=slot_id, hours_from_now=48 + slot_id))

        booking = service.book_slot(user_id=1, slot_id=slot_id)

        assert booking.slot_id == slot_id
