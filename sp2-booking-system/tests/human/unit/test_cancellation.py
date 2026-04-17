import pytest
from freezegun import freeze_time

from services import BookingError
from tests.human.unit.conftest import NOW
from tests.factories.slot_factory import create_slot


TOO_LATE_HOURS = 12


class TestCancellation:

    @freeze_time(NOW)
    def test_successful_cancellation(self, service, repo):
        slot = create_slot()
        repo.add_slot(slot)

        booking = service.book_slot(user_id=1, slot_id=1)
        result = service.cancel_booking(user_id=1, booking_id=booking.id)

        assert result.status.value == "CANCELLED"
        assert repo.get_slot(1).status.name == "AVAILABLE"

    @freeze_time(NOW)
    def test_late_cancellation_rejected(self, service, repo):
        slot = create_slot(hours_from_now=TOO_LATE_HOURS)
        repo.add_slot(slot)

        booking = service.book_slot(user_id=1, slot_id=1)

        with pytest.raises(BookingError, match="Cancellation too late"):
            service.cancel_booking(user_id=1, booking_id=booking.id)

    @freeze_time(NOW)
    def test_cannot_cancel_foreign_booking(self, service, repo):
        slot = create_slot()
        repo.add_slot(slot)

        booking = service.book_slot(user_id=1, slot_id=1)

        with pytest.raises(BookingError, match="User cannot cancel чужую booking"):
            service.cancel_booking(user_id=2, booking_id=booking.id)

    @freeze_time(NOW)
    def test_slot_restored_after_cancellation(self, service, repo):
        slot = create_slot()
        repo.add_slot(slot)

        booking = service.book_slot(user_id=1, slot_id=1)
        service.cancel_booking(user_id=1, booking_id=booking.id)

        restored_slot = repo.get_slot(1)
        assert restored_slot.status.name == "AVAILABLE"

    @freeze_time(NOW)
    def test_cancelling_nonexistent_booking_raises(self, service):
        with pytest.raises(BookingError, match="Booking does not exist"):
            service.cancel_booking(user_id=1, booking_id=999)
