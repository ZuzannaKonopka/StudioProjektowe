"""
    test_consistency.py

    Testy spójności systemu (SDLC consistency layer).

    Cel:
    - sprawdzenie zgodności między warstwami systemu:
    repository ↔ service ↔ booking state
    - analiza czy operacje nie powodują rozjazdów stanu
    - weryfikacja propagacji zmian w systemie

    To są kluczowe testy dla:
    - pytania badawczego o consistency (SDLC)
    - analizy propagacji błędów
"""

from models import SlotStatus


def test_booking_consistency_between_repo_and_service(service, repo, slot_factory):
    """
        Sprawdza czy booking poprawnie aktualizuje stan repozytorium.
    """
    slot = slot_factory(1, 10, 48)
    repo.add_slot(slot)

    booking = service.book_slot(user_id=1, slot_id=1)

    # consistency check: service ↔ repository
    assert repo.get_slot(1).status == SlotStatus.BOOKED
    assert booking.slot_id == slot.id


def test_cancellation_consistency(service, repo, slot_factory):
    """
        Sprawdza czy cancel synchronizuje stan systemu.
    """
    slot = slot_factory(1, 10, 48)
    repo.add_slot(slot)

    booking = service.book_slot(user_id=1, slot_id=1)
    service.cancel_booking(user_id=1, booking_id=booking.id)

    assert repo.get_slot(1).status == SlotStatus.AVAILABLE


def test_user_bookings_consistency(service, repo, slot_factory):
    """
        Sprawdza spójność widoku użytkownika z repozytorium.
    """
    slot = slot_factory(1, 10, 48)
    repo.add_slot(slot)

    booking = service.book_slot(user_id=1, slot_id=1)

    user_bookings = repo.get_user_bookings(1)

    assert len(user_bookings) == 1
    assert user_bookings[0].id == booking.id


def test_state_consistency_after_multiple_operations(service, repo, slot_factory):
    """
        Test systemowy:
        sprawdza czy wieloetapowe operacje nie psują stanu systemu.
    """
    slot = slot_factory(1, 10, 48)
    repo.add_slot(slot)

    booking = service.book_slot(user_id=1, slot_id=1)
    service.cancel_booking(user_id=1, booking_id=booking.id)
    
    assert len(repo.get_user_bookings(1)) == 1
    assert repo.get_user_bookings(1)[0].status.value == "CANCELLED"

    