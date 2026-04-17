from tests.factories.slot_factory import create_slot


class TestAvailability:

    def test_returns_only_available_slots(self, service, repo):
        s1 = create_slot(slot_id=1)
        s2 = create_slot(slot_id=2)
        s2.status = s2.status.BOOKED

        repo.add_slot(s1)
        repo.add_slot(s2)

        result = service.get_available_slots(10, s1.start_time.date())

        assert len(result) == 1
        assert result[0].id == 1

    def test_returns_empty_when_no_slots(self, service):
        result = service.get_available_slots(10, service.repo.slots.get(1, None))
        assert result == []

    def test_filters_by_specialist(self, service, repo):
        s1 = create_slot(slot_id=1, specialist_id=10)
        s2 = create_slot(slot_id=2, specialist_id=20)

        repo.add_slot(s1)
        repo.add_slot(s2)

        result = service.get_available_slots(10, s1.start_time.date())

        assert len(result) == 1
        assert result[0].specialist_id == 10
