"""
Unit tests for the MultiMonitorManager subsystem.
"""

from ikkhi.vision.monitors import MultiMonitorManager, MonitorInfo


def test_monitor_enumeration():
    mgr = MultiMonitorManager()
    monitors = mgr.get_all_monitors()
    assert len(monitors) >= 1, "At least one primary display monitor should be detected."
    primary = next((m for m in monitors if m.is_primary), None)
    assert primary is not None, "Primary display must be identified."
    assert primary.width > 0
    assert primary.height > 0


def test_cursor_monitor_resolution():
    mgr = MultiMonitorManager()
    active_mon = mgr.get_cursor_monitor()
    assert isinstance(active_mon, MonitorInfo)
    assert active_mon.width > 0
    assert active_mon.height > 0
