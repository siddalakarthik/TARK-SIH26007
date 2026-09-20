from app.hardware.encoder_contract import EncoderContract
from app.hardware.simulators import ESP32EncoderAdapter


def test_count_contract_reports_wheel_response_without_assuming_speed_or_hardware():
    contract = EncoderContract()
    first = contract.accept(10, -5, 100, "SIMULATION")
    second = contract.accept(14, -3, 200, "SIMULATION")
    assert first.state == "SIMULATION" and first.left_delta == first.right_delta == 0
    assert (second.left_delta, second.right_delta) == (4, 2)
    assert contract.health(250, 100).state == "SIMULATION"
    assert contract.health(301, 100).state == "STALE"


def test_count_contract_handles_explicit_wrap_and_rejects_invalid_jumps_and_timestamps():
    contract = EncoderContract(counter_modulus=256, max_count_delta=20)
    assert contract.accept(250, 2, 100, "REAL").state == "ONLINE"
    wrapped = contract.accept(3, 254, 200, "REAL")
    assert (wrapped.left_delta, wrapped.right_delta) == (9, -4)
    assert contract.accept(100, 100, 300, "REAL").reason == "IMPOSSIBLE_ENCODER_COUNT_JUMP"
    assert contract.accept(4, 253, 200, "REAL").reason == "NON_MONOTONIC_ENCODER_TIMESTAMP"
    assert contract.health(400, 10).state == "STALE"


def test_count_contract_is_truthful_when_no_real_encoder_is_connected():
    contract = EncoderContract()
    assert contract.health(0, 1).state == "NO_DATA"
    assert contract.accept(0, 0, 1, "NOT_CONNECTED").state == "NOT_CONNECTED"
    assert contract.accept(True, 0, 1, "REAL").state == "INVALID"


def test_esp32_encoder_adapter_exposes_counts_without_converting_to_ground_speed():
    adapter = ESP32EncoderAdapter(EncoderContract())
    adapter.ingest_counts(12, 13, 50, "REAL")
    response = adapter.read_wheel_response(51)
    assert (response.left_count, response.right_count, response.left_mps, response.right_mps) == (12, 13, None, None)
    assert response.source_mode == "REAL" and response.reason == "WHEEL_RESPONSE_COUNTS_ONLY"
