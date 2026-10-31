from mantagu.config import MantaguConfig
from mantagu.pipeline import ManTAGUPipeline


def test_mock_stream():
    pipe = ManTAGUPipeline(MantaguConfig())
    frames = pipe.stream_mock(frames=3)
    assert len(frames) == 3
    assert "pose" in frames[0]
    assert "fusion" in frames[0]
    assert frames[0]["node_id"] == "ManTAGU-Vector-01"
