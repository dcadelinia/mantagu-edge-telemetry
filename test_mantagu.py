from __future__ import annotations

from mantagu.config import load_config, load_project_identity
from mantagu.fusion import run_gpu_sensor_fusion_batch
from mantagu.packets import parse_raw_stream
from mantagu.pipeline import ManTAGUPipeline


def test_identity():
    ident = load_project_identity("config.json")
    assert "ManTAGU" in ident["project_identity"]["system_name"]


def test_parse_packet():
    line = "MANTAGU_DATA:1000,0.1,-0.2,9.9,2000,0.55"
    pkt = parse_raw_stream(line)
    assert pkt is not None
    assert pkt.surface_compliance == 2000
    assert parse_raw_stream("NOPE") is None


def test_pipeline_stream():
    cfg = load_config("config/mantagu.yaml")
    pipe = ManTAGUPipeline(cfg)
    out = pipe.stream_to_sim_environment(frames=4, sleep_s=0.0)
    assert len(out) == 4
    assert "pose_x" in out[0]


def test_fusion():
    result = run_gpu_sensor_fusion_batch(batch_size=64, seed=2)
    assert result["batch_size"] == 64
    assert "slip_index_0" in result
