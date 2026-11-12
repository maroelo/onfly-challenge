"""Regressão: top_hotels por total_brl decrescente, empate por hotel_id crescente (README, Ordenação)."""

from helpers import run_cli


def _hotel(index, hotel_id, amount):
    return {"reservation_id": f"R-{index}", "hotel_id": hotel_id, "hotel_name": f"Hotel {hotel_id}", "amount": amount}


def test_highest_total_first_with_same_digit_count(tmp_path):
    # Mesma quantidade de dígitos: o erro não depende de ordenação textual.
    report = run_cli(tmp_path, [_hotel(1, "H02", "900.00"), _hotel(2, "H01", "950.00")], top=1)

    assert [(h["hotel_id"], h["total_brl"]) for h in report["top_hotels"]] == [("H01", "950.00")]


def test_numeric_not_string_order_and_top_n_cut(tmp_path):
    # "900.00" > "1000.00" como texto; o README exige ordem numérica.
    report = run_cli(
        tmp_path,
        [_hotel(1, "H03", "900.00"), _hotel(2, "H01", "1000.00"), _hotel(3, "H02", "99.99")],
        top=2,
    )

    assert [(h["hotel_id"], h["total_brl"]) for h in report["top_hotels"]] == [("H01", "1000.00"), ("H03", "900.00")]


def test_tie_breaks_by_hotel_id_ascending(tmp_path):
    report = run_cli(
        tmp_path,
        [_hotel(1, "H03", "500.00"), _hotel(2, "H02", "500.00"), _hotel(3, "H01", "700.00")],
        top=3,
    )

    assert [h["hotel_id"] for h in report["top_hotels"]] == ["H01", "H02", "H03"]
