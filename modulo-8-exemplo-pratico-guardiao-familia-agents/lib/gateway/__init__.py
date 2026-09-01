"""Gateway de status, handoff e eventos (v2 role-based)."""
from lib.gateway.gateway import *  # noqa: F403
from lib.gateway.handoff import load_handoff, write_handoff
from lib.gateway.hitl_gates import *  # noqa: F403
from lib.gateway.v2_events import is_valid_gateway_event, legacy_event_error  # noqa: F401
from lib.gateway.actuation_guardrail import (  # noqa: F401
    consume_guard_pass,
    evaluate_actuation_guard,
    load_guardrail_policy,
    validate_guard_pass,
)
