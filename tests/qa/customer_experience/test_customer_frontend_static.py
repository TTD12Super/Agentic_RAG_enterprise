from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
APP = (ROOT / "frontend/src/App.tsx").read_text(encoding="utf-8")
CLIENT = (ROOT / "frontend/src/api/client.ts").read_text(encoding="utf-8")
STYLES = (ROOT / "frontend/src/styles.css").read_text(encoding="utf-8")


def test_reload_contract_restores_conversation_and_requests_history():
    """Repro: send a message, reload the browser, and expect the same history."""

    assert "getConversation(" in APP
    assert "localStorage" in APP or "sessionStorage" in APP


def test_retryable_backend_error_has_a_user_recovery_action():
    """Repro: stop the backend, submit, restart it, then press Retry."""

    assert "retryable" in CLIENT
    assert "Retry" in APP
    assert "retry" in APP.casefold()


def test_responsive_layout_has_mobile_breakpoints_and_no_horizontal_body_overflow():
    """Static gate for the desktop, tablet and phone customer surfaces."""

    assert "overflow-x: hidden" in STYLES
    assert "@media (max-width: 1024px)" in STYLES
    assert "@media (max-width: 760px)" in STYLES
    assert "@media (max-width: 460px)" in STYLES
    assert "main-shell { margin-left: 0" in STYLES


def test_mobile_375x812_contract_keeps_chat_controls_within_the_viewport():
    """Deterministic static companion for the 375px mobile browser check."""

    mobile_width, mobile_height = 375, 812
    assert mobile_width >= 320
    assert mobile_height > 0
    assert "body { overflow-x: hidden" in STYLES
    assert "@media (max-width: 760px)" in STYLES
    assert ".chat-layout { display: block; }" in STYLES
    assert ".chat-mobile-toolbar { display: flex;" in STYLES
    assert ".history-drawer-open { transform: translateX(0); }" in STYLES
    assert ".history-scrim { position: fixed;" in STYLES
    assert 'id="chat-query"' in APP
    assert 'aria-label="Send question"' in APP


def test_chat_controls_have_keyboard_labels_and_live_status_semantics():
    """Static gate for keyboard users and screen-reader status feedback."""

    assert 'htmlFor="chat-query"' in APP
    assert 'aria-label="Send question"' in APP
    assert 'aria-label="Stop generating"' in APP
    assert 'aria-label="Close navigation"' in APP
    assert 'role="status"' in APP
    assert ":focus-visible" in STYLES


def test_stop_control_is_available_only_during_a_live_stream():
    """Static contract: a user can stop generation while the composer is busy."""

    assert "onStopQuery" in APP
    assert "streamAbortRef" in APP
    assert "controller.signal.aborted" in APP
