"""
    test_booking_business_rules.py

    Testy reguł biznesowych systemu.

    Cel:
    - weryfikacja logiki biznesowej
    - sprawdzenie ograniczeń systemowych

    Zakres:
    - limit rezerwacji
    - blokada podwójnej rezerwacji
    - kontrolapip dostępu (anulowanie cudzej rezerwacji)
"""

import pytest
from services import BookingError


def test_booking_limit_enforced(service, repo, slot_factory):
    """
        Użytkownik nie może mieć więcej niż 3 aktywne rezerwacje.
    """
    for i in range(1, 5):
        slot = slot_factory(i, 10, 48 + i)
        repo.add_slot(slot)

    service.book_slot(user_id=1, slot_id=1)
    service.book_slot(user_id=1, slot_id=2)
    service.book_slot(user_id=1, slot_id=3)

    with pytest.raises(BookingError):
        service.book_slot(user_id=1, slot_id=4)


def test_double_booking_prevented(service, repo, slot_factory):
    """
        Ten sam slot nie może być zarezerwowany przez dwóch użytkowników.
    """
    slot = slot_factory(1, 10, 48)
    repo.add_slot(slot)

    service.book_slot(user_id=1, slot_id=1)

    with pytest.raises(BookingError):
        service.book_slot(user_id=2, slot_id=1)

def test_same_user_cannot_book_same_slot_twice(service, repo, slot_factory):
    """
        Ten sam slot nie może być zduplikowany przez tego samego użytkownika
    """
    slot = slot_factory(1, 10, 48)
    repo.add_slot(slot)

    service.book_slot(user_id=1, slot_id=1)

    with pytest.raises(BookingError):
        service.book_slot(user_id=1, slot_id=1)

def test_cannot_cancel_foreign_booking(service, repo, slot_factory):
    """
        Użytkownik nie może anulować rezerwacji innego użytkownika.
    """
    slot = slot_factory(1, 10, 48)
    repo.add_slot(slot)

    booking = service.book_slot(user_id=1, slot_id=1)

    with pytest.raises(BookingError):
        service.cancel_booking(user_id=2, booking_id=booking.id)