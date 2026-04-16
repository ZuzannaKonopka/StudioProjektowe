"""
    conftest.py

    Plik konfiguracyjny dla pytest.
    Zawiera wspólne fixtures wykorzystywane w całym zestawie testów.

    Cel:
    - eliminacja duplikacji kodu (DRY)
    - standaryzacja środowiska testowego
    - łatwe tworzenie danych testowych

    Fixtures:
    - repo: in-memory repozytorium danych
    - service: warstwa serwisowa systemu rezerwacji
    - slot_factory: generator obiektów Slot (test data factory)
"""

from datetime import datetime, timedelta
import pytest
from models import Slot, SlotStatus
from repository import InMemoryRepository
from services import BookingService


@pytest.fixture
def repo():
    """Tworzy świeże repozytorium dla każdego testu."""
    return InMemoryRepository()


@pytest.fixture
def service(repo):
    """Tworzy instancję serwisu korzystającą z repozytorium."""
    return BookingService(repo)


@pytest.fixture
def slot_factory():
    """
        Factory do tworzenia slotów czasowych.

        Parametry:
        - slot_id: identyfikator slotu
        - specialist_id: ID specjalisty
        - hours_from_now: ile godzin od teraz zaczyna się slot

        Zwraca:
        - obiekt Slot w stanie AVAILABLE
    """
    def _make(slot_id: int, specialist_id: int, hours_from_now: int):
        start = datetime.utcnow() + timedelta(hours=hours_from_now)
        end = start + timedelta(minutes=30)
        return Slot(
            id=slot_id,
            specialist_id=specialist_id,
            start_time=start,
            end_time=end,
            status=SlotStatus.AVAILABLE,
        )
    return _make