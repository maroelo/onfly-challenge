"""Regressão: noites = (checkout - checkin).days * rooms, também na virada de ano (README, seção Noites)."""

from helpers import run_cli


def test_room_nights_across_year_boundary_with_multiple_rooms(tmp_path):
    # 2024-12-30 -> 2025-01-02 = 3 noites; 2 quartos -> 6 noites de quarto
    report = run_cli(
        tmp_path,
        [{"reservation_id": "R-1", "checkin_date": "2024-12-30", "checkout_date": "2025-01-02", "rooms": "2"}],
    )

    assert report["summary"]["total_room_nights"] == 6
    assert report["by_month"][0]["month"] == "2024-12"
    assert report["by_month"][0]["room_nights"] == 6
    assert report["top_hotels"][0]["room_nights"] == 6


def test_room_nights_sum_across_months_by_checkin(tmp_path):
    # README: by_month usa o mês do check-in; 01-28 -> 02-02 = 5 noites * 2 quartos = 10, tudo em 2025-01
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "checkin_date": "2025-01-28", "checkout_date": "2025-02-02", "rooms": "2"},
            {"reservation_id": "R-2", "checkin_date": "2025-02-05", "checkout_date": "2025-02-08", "rooms": "1"},
        ],
    )

    assert report["summary"]["total_room_nights"] == 13
    assert [(m["month"], m["room_nights"]) for m in report["by_month"]] == [("2025-01", 10), ("2025-02", 3)]
