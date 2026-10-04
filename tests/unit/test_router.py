"""
Unit tests for the Ikkhi IntentRouter (Tier 0 local fast path vs Tier 1 cloud AI).
"""

from ikkhi.core.router import IntentRouter, RouteTarget


def test_local_media_fast_path():
    router = IntentRouter()
    route = router.route("play")
    assert route.target == RouteTarget.LOCAL_ACTION
    assert route.action_name == "media_play_pause"
    assert route.is_cloud_request is False


def test_davinci_actions_fast_path():
    router = IntentRouter()
    
    route_cut = router.route("cut clip")
    assert route_cut.target == RouteTarget.LOCAL_ACTION
    assert route_cut.action_name == "davinci_blade_cut"
    assert route_cut.is_cloud_request is False

    route_ripple = router.route("ripple delete")
    assert route_ripple.target == RouteTarget.LOCAL_ACTION
    assert route_ripple.action_name == "davinci_ripple_delete"


def test_visual_query_classification():
    router = IntentRouter()
    route = router.route("where is the export button")
    assert route.target == RouteTarget.VISUAL_QUERY
    assert route.is_cloud_request is True


def test_conversational_fallback():
    router = IntentRouter()
    route = router.route("how do I color grade a sunset?")
    assert route.target == RouteTarget.CONVERSATIONAL_FALLBACK
    assert route.is_cloud_request is True
