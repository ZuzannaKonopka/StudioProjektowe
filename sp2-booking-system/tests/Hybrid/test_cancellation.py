"""
    test_cancellation.py

    Testy logiki anulowania rezerwacji w systemie bookingowym.

    Cel:
    - weryfikacja poprawności procesu anulowania
    - sprawdzenie reguł biznesowych (np. limit czasowy anulacji)
    - kontrola stanu systemu po operacjach cancel

    Kategorie:
    - successful cancellation
    - business rule enforcement (late cancellation)
    - state restoration
    - idempotency (double cancel prevention)
"""

import pytest
from services import BookingError
from models import SlotStatus


def test_successful_cancellation(service, repo, slot_factory):
    """
        Poprawne anulowanie rezerwacji:
        - booking zostaje oznaczony jako CANCELLED
        - slot wraca do AVAILABLE
    """
    slot = slot_factory(1, 10, 48)
    repo.add_slot(slot)

    booking = service.book_slot(user_id=1, slot_id=1)
    result = service.cancel_booking(user_id=1, booking_id=booking.id)

    assert result.status.value == "CANCELLED"
    assert repo.get_slot(1).status == SlotStatus.AVAILABLE


def test_late_cancellation_rejected(service, repo, slot_factory):
    """
        System powinien odrzucać anulowanie po przekroczeniu limitu czasowego.
    """
    slot = slot_factory(1, 10, 12)
    repo.add_slot(slot)

    booking = service.book_slot(user_id=1, slot_id=1)

    with pytest.raises(BookingError):
        service.cancel_booking(user_id=1, booking_id=booking.id)


def test_slot_restored_after_cancellation(service, repo, slot_factory):
    """
        Po anulowaniu slot powinien wrócić do stanu AVAILABLE.
    """
    slot = slot_factory(1, 10, 48)
    repo.add_slot(slot)

    booking = service.book_slot(user_id=1, slot_id=1)
    service.cancel_booking(user_id=1, booking_id=booking.id)

    restored_slot = repo.get_slot(1)
    assert restored_slot.status == SlotStatus.AVAILABLE


def test_cannot_cancel_twice(service, repo, slot_factory):
    """
        Idempotency check:
        anulowanie tej samej rezerwacji dwa razy powinno być błędem.
    """
    slot = slot_factory(1, 10, 48)
    repo.add_slot(slot)

    booking = service.book_slot(user_id=1, slot_id=1)
    service.cancel_booking(user_id=1, booking_id=booking.id)

    with pytest.raises(BookingError):
        service.cancel_booking(user_id=1, booking_id=booking.id)