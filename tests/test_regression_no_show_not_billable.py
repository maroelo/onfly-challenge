"""Regressão: NO_SHOW conta no total, mas não é faturável (README, seção Status)."""

from helpers import run_cli


def test_no_show_alone_is_counted_but_not_billed(tmp_path):
    report = run_cli(tmp_path, [{"reservation_id": "R-1", "status": "NO_SHOW", "amount": "300.00"}])

    assert report["summary"] == {
        "total_reservations": 1,
        "confirmed_reservations": 0,
        "cancelled_reservations": 0,
        "no_show_reservations": 1,
        "total_room_nights": 0,
        "total_amount_brl": "0.00",
        "average_nightly_rate_brl": "0.00",
    }
    assert report["by_month"] == []
    assert report["top_hotels"] == []


def test_no_show_does_not_leak_into_by_month_or_top_hotels(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "hotel_name": "Hotel A", "amount": "100.00"},
            {
                "reservation_id": "R-2",
                "hotel_id": "H02",
                "hotel_name": "Hotel B",
                "status": "NO_SHOW",
                "amount": "900.00",
                "checkin_date": "2025-02-10",
                "checkout_date": "2025-02-11",
            },
        ],
    )

    assert report["by_month"] == [
        {"month": "2025-01", "reservations": 1, "room_nights": 1, "total_brl": "100.00"}
    ]
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01"]
