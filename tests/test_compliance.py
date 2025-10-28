from src.bot.compliance.loop_detector import LoopDetector

def test_loop_detector():
    ld = LoopDetector(1500)
    assert not ld.ok(1000, 2000)
    assert ld.ok(1000, 2600)
