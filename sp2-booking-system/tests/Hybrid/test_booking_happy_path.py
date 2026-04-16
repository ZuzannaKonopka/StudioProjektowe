"""
    test_booking_happy_path.py

    Testy scenariuszy podstawowych (happy path).

    Cel:
    - sprawdzenie czy system działa poprawnie w standardowych przypadkach
    - brak błędów wejściowych i edge cases

    Zakres:
    - pobieranie dostępnych slotów
    - poprawna rezerwacja
"""

from models import SlotStatus


def test_get_available_slots_returns_only_available(service, repo, slot_factory):
    """
        Sprawdza czy zwracane są tylko dostępne sloty.
    """
    s1 = slot_factory(1, 10, 48)
    s2 = slot_factory(2, 10, 72)
    s2.status = SlotStatus.BOOKED

    repo.add_slot(s1)
    repo.add_slot(s2)

    slots = service.get_available_slots(10, s1.start_time.date())

    assert len(slots) == 1
    assert slots[0].id == 1


def test_successful_booking(service, repo, slot_factory):
    """
        Sprawdza czy poprawna rezerwacja:
        - zwraca właściwe dane
        - zmienia status slotu na BOOKED
    """
    slot = slot_factory(1, 10, 48)
    repo.add_slot(slot)

    booking = service.book_slot(user_id=1, slot_id=1)

    assert booking.user_id == 1
    assert booking.slot_id == 1
    assert repo.get_slot(1).status == SlotStatus.BOOKED