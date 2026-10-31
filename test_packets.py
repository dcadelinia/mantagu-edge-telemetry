from mantagu.packets import parse_raw_stream


def test_parse_valid():
    line = "MANTAGU_DATA:1710000000000,0.23,-0.12,9.81,2500,0.78"
    pkt = parse_raw_stream(line)
    assert pkt is not None
    assert pkt.timestamp_ms == 1710000000000
    assert abs(pkt.acceleration_z - 9.81) < 1e-6
    assert abs(pkt.micro_friction_index - 0.78) < 1e-6


def test_parse_invalid():
    assert parse_raw_stream("NOPE") is None
    assert parse_raw_stream("MANTAGU_DATA:1,2") is None
