"""Regressão: total_reservations é o número de reservas no arquivo, sem limite de linhas (README, Totais)."""

from helpers import run_cli


def test_all_rows_are_read_beyond_200(tmp_path):
    # 250 reservas confirmadas de 100.00 BRL, 1 noite cada.
    rows = [{"reservation_id": f"R-{index}"} for index in range(1, 251)]

    report = run_cli(tmp_path, rows)

    assert report["summary"]["total_reservations"] == 250
    assert report["summary"]["confirmed_reservations"] == 250
    assert report["summary"]["total_room_nights"] == 250
    assert report["summary"]["total_amount_brl"] == "25000.00"


def test_last_row_of_the_file_is_counted(tmp_path):
    # A última linha (a 201ª) é a única CANCELLED; se for descartada, a contagem por status fica errada.
    rows = [{"reservation_id": f"R-{index}"} for index in range(1, 201)]
    rows.append({"reservation_id": "R-201", "status": "CANCELLED"})

    report = run_cli(tmp_path, rows)

    assert report["summary"]["total_reservations"] == 201
    assert report["summary"]["cancelled_reservations"] == 1
