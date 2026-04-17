from datetime import datetime
import pytest

from repository import InMemoryRepository
from services import BookingService


NOW = datetime(2026, 4, 10, 8, 0, 0)


@pytest.fixture
def repo():
    return InMemoryRepository()


@pytest.fixture
def service(repo):
    return BookingService(repo)
