import pytest

from app.sensors.ld2450.parser import FrameError, LD2450Parser


def signed_magnitude(value: int) -> bytes:
    raw = abs(value) | (0x8000 if value >= 0 else 0)
    return raw.to_bytes(2, "little")


def report(*targets: tuple[int, int, int, int] | None) -> bytes:
    slots = list(targets) + [None] * (3 - len(targets))
    body = bytearray(LD2450Parser.HEADER)
    for target in slots:
        if target is None:
            body.extend(b"\0" * 8)
            continue
        x_mm, y_mm, speed_cmps, resolution_mm = target
        body.extend(signed_magnitude(x_mm))
        body.extend(signed_magnitude(y_mm))
        body.extend(signed_magnitude(speed_cmps))
        body.extend(resolution_mm.to_bytes(2, "little"))
    return bytes(body) + LD2450Parser.FOOTER


def test_published_style_target_report_decodes_sign_magnitude_and_units():
    # Matches the published field encoding: negative x/speed; positive y.
    detections = LD2450Parser().parse(report((-782, 1713, -16, 320)), 123)
    assert len(detections) == 1
    item = detections[0]
    assert (item.candidate_id, item.x_m, item.y_m, item.velocity_mps) == (1, -0.782, 1.713, -0.16)
    assert item.uncertainty_m == 0.32 and item.quality == 0.0 and item.timestamp_ns == 123


def test_empty_and_multiple_target_slots_are_preserved_without_invented_ids():
    detections = LD2450Parser().parse(report(None, (1000, -500, 125, 20), (-50, 50, 0, 10)), 9)
    assert [(item.candidate_id, item.x_m, item.y_m, item.velocity_mps) for item in detections] == [
        (2, 1.0, -0.5, 1.25), (3, -0.05, 0.05, 0.0),
    ]


def test_incremental_decoder_accepts_noise_partial_and_concatenated_reports():
    parser = LD2450Parser()
    first = report((100, 200, 0, 10))
    second = report((200, 300, -10, 20))
    assert parser.feed(b"noise" + first[:11], 1) == []
    decoded = parser.feed(first[11:] + second, 2)
    assert [[item.x_m for item in result] for result in decoded] == [[0.1], [0.2]]
    assert parser.valid_frame_count == 2 and parser.rejected_frame_count == 0


def test_malformed_footer_truncated_frame_and_out_of_range_target_are_rejected():
    parser = LD2450Parser()
    with pytest.raises(FrameError, match="INVALID_LD2450_LENGTH"):
        parser.parse(report((100, 100, 0, 1))[:-1], 1)
    bad_footer = bytearray(report((100, 100, 0, 1))); bad_footer[-1] = 0
    assert parser.feed(bytes(bad_footer), 2) == []
    assert parser.rejected_frame_count >= 1
    with pytest.raises(FrameError, match="IMPOSSIBLE_LD2450_RANGE"):
        LD2450Parser().parse(report((6000, 6000, 0, 1)), 1)
