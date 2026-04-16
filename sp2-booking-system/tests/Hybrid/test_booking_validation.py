"""
    test_booking_validation.py

    Testy walidacji danych wejściowych.

    Cel:
    - sprawdzenie odporności systemu na niepoprawne dane
    - weryfikacja obsługi błędów (exception handling)

    Zakres:
    - nieistniejące sloty i bookingi
    - niepoprawne user_id (None, typy błędne)
    - niepoprawne slot_id

    Znaczenie w projekcie:
    - LLM często pomija walidację → ten plik jest kluczowy dla podejścia HYBRID
"""

import pytest
from services import BookingError


def test_booking_non_existing_slot(service):
    """
        Próba rezerwacji nieistniejącego slotu powinna zakończyć się błędem.
    """
    with pytest.raises(BookingError):
        service.book_slot(user_id=1, slot_id=999)


def test_cancel_non_existing_booking(service):
    """
        Próba anulowania nieistniejącej rezerwacji powinna zakończyć się błędem.
    """
    with pytest.raises(BookingError):
        service.cancel_booking(user_id=1, booking_id=999)

def test_booking_with_missing_slot_in_repo(service):
    """
        Próba rezerwacji poprawnego slotu, której brak w repo powinna zakończyć się błędem.
    """
    with pytest.raises(BookingError):
        service.book_slot(user_id=1, slot_id=1)

@pytest.mark.parametrize("user_id", [None, -1, "abc"])
def test_invalid_user_id(service, repo, slot_factory, user_id):
    """
        Test walidacji user_id:
        - None
        - liczby ujemne
        - niepoprawne typy (string)

        System powinien odrzucić wszystkie niepoprawne wartości.
    """
    slot = slot_factory(1, 10, 48)
    repo.add_slot(slot)

    with pytest.raises(BookingError):
        service.book_slot(user_id=user_id, slot_id=1)


@pytest.mark.parametrize("slot_id", [None, -1, "invalid"])
def test_invalid_slot_id(service, slot_id):
    """
        Test walidacji slot_id:
        - None
        - liczby ujemne
        - niepoprawne typy

        System powinien zgłosić błąd dla niepoprawnych identyfikatorów slotów.
    """
    with pytest.raises(BookingError):
        service.book_slot(user_id=1, slot_id=slot_id)