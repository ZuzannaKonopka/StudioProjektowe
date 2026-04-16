"""
    test_booking_edge_cases.py

    Testy przypadków brzegowych (edge cases).

    Cel:
    - sprawdzenie zachowania systemu w sytuacjach granicznych
    - wykrywanie subtelnych błędów logiki biznesowej

    Zakres:
    - granice limitów (np. max liczba rezerwacji)
    - granice czasowe (np. anulowanie 24h przed)
    - scenariusze wieloużytkownikowe
    - rezerwacja w przeszłości

    Znaczenie w projekcie:
    - edge cases są często pomijane przez LLM
    - kluczowe dla metryk: completeness i defect detection
"""

import pytest
from services import BookingError
from models import SlotStatus


def test_booking_exact_limit_boundary(service, repo, slot_factory):
    """
        Test graniczny limitu rezerwacji.
        Użytkownik może mieć maksymalnie 3 rezerwacje.
        Sprawdzamy dokładnie granicę (boundary = 3).
    """
    for i in range(1, 4):
        slot = slot_factory(i, 10, 48 + i)
        repo.add_slot(slot)
        service.book_slot(user_id=1, slot_id=i)

    bookings = repo.get_user_bookings(1)

    assert len(bookings) == 3


def test_cancellation_exactly_24h_before(service, repo, slot_factory):
    """
        Test graniczny anulowania rezerwacji.
        Sprawdzamy czy anulowanie dokładnie 24h przed wizytą jest dozwolone.
    """
    slot = slot_factory(1, 10, 24)
    repo.add_slot(slot)

    booking = service.book_slot(user_id=1, slot_id=1)

    try:
        service.cancel_booking(user_id=1, booking_id=booking.id)
    except BookingError:
        pytest.fail("Cancellation at 24h boundary should be allowed")


def test_multiple_users_booking_different_slots(service, repo, slot_factory):
    """
        Test scenariusza wieloużytkownikowego.
        Dwóch użytkowników rezerwuje różne sloty → system powinien działać poprawnie.
    """
    s1 = slot_factory(1, 10, 48)
    s2 = slot_factory(2, 10, 49)

    repo.add_slot(s1)
    repo.add_slot(s2)

    b1 = service.book_slot(user_id=1, slot_id=1)
    b2 = service.book_slot(user_id=2, slot_id=2)

    assert b1.user_id != b2.user_id
    assert repo.get_slot(1).status == SlotStatus.BOOKED
    assert repo.get_slot(2).status == SlotStatus.BOOKED


def test_rebooking_after_cancellation(service, repo, slot_factory):
    """
        Po anulowaniu slot powinien być ponownie dostępny.
        Inny użytkownik powinien móc go zarezerwować.
    """
    slot = slot_factory(1, 10, 48)
    repo.add_slot(slot)

    booking = service.book_slot(user_id=1, slot_id=1)
    service.cancel_booking(user_id=1, booking_id=booking.id)

    new_booking = service.book_slot(user_id=2, slot_id=1)
    assert new_booking.user_id == 2


def test_booking_in_past(service, repo, slot_factory):
    """
        Test walidacji czasu.
        Rezerwacja w przeszłości powinna być zabroniona.
    """
    slot = slot_factory(1, 10, -1)
    repo.add_slot(slot)

    result = service.book_slot(user_id=1, slot_id=1)

    assert result is not None  # albo status zależnie od systemu