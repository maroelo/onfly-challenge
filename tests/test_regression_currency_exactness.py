"""Regressão: câmbio = amount * rate_to_brl, exato em Decimal, half-up só na serialização (README, Câmbio/Exatidão)."""

from helpers import run_cli


def test_conversion_multiplies_by_rate(tmp_path):
    # 100.00 USD * 5.42 = 542.00 BRL (não 100 / 5.42 = 18.45)
    report = run_cli(tmp_path, [{"currency": "USD", "amount": "100.00"}])

    assert report["summary"]["total_amount_brl"] == "542.00"


def test_conversion_is_exact_before_half_up(tmp_path):
    # 0.75 USD * 5.42 = 4.065 exato -> half-up = 4.07.
    # Via float, 0.75 * 5.42 = 4.0649999999999995 -> 4.06.
    report = run_cli(tmp_path, [{"currency": "USD", "amount": "0.75"}])

    assert report["summary"]["total_amount_brl"] == "4.07"
    assert report["by_month"][0]["total_brl"] == "4.07"
    assert report["top_hotels"][0]["total_brl"] == "4.07"
