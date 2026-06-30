"""Tests for LLMToolSelectorMiddleware integration."""

from unittest.mock import MagicMock, patch

from tyqa.middleware.tool_selector import (
    _ConditionalToolSelectorMiddleware,
    _ToolSelectionTrackerMiddleware,
    create_tool_selector_middleware,
)


def _mock_model():
    """Create a MagicMock model compatible with disable_thinking()."""
    m = MagicMock(profile={"max_input_tokens": 200_000})
    m.thinking = None
    m.reasoning = None
    return m


def _patched_create():
    """Create tool selector middleware without real LLM init."""
    return [
        _ConditionalToolSelectorMiddleware(MagicMock(), threshold=20),
        _ToolSelectionTrackerMiddleware(),
    ]


# Helper: patches needed to call create_tool_selector_middleware without LLM
def _factory_patches():
    return (
        patch(
            "tyqa.middleware.tool_selector.disable_thinking",
            return_value=MagicMock(),
            create=True,
        ),
        patch("tyqa.agent_graph._ensure_chat_model", return_value=MagicMock()),
        patch(
            "langchain.agents.middleware.LLMToolSelectorMiddleware",
            return_value=MagicMock(),
        ),
    )


# ---------------------------------------------------------------------------
# Factory tests
# ---------------------------------------------------------------------------


def test_create_tool_selector_returns_list():
    p1, p2, p3 = _factory_patches()
    with p1, p2, p3:
        result = create_tool_selector_middleware()
        assert isinstance(result, list)
        assert len(result) == 2


def test_create_tool_selector_can_disable_stream_tracking():
    p1, p2, p3 = _factory_patches()
    with p1, p2, p3:
        result = create_tool_selector_middleware(track_stream_selection=False)
        assert isinstance(result, list)
        assert len(result) == 1
        assert type(result[0]).__name__ == "_ConditionalToolSelectorMiddleware"


def test_create_tool_selector_always_include():
    p1, p2, p3 = _factory_patches()
    with p1, p2, p3 as mock_cls:
        create_tool_selector_middleware()
        mock_cls.assert_called_once()
        call_kwargs = mock_cls.call_args[1]
        assert "think_tool" in call_kwargs["always_include"]
        assert "task" in call_kwargs["always_include"]


def test_custom_threshold():
    p1, p2, p3 = _factory_patches()
    with p1, p2, p3:
        result = create_tool_selector_middleware(threshold=5)
        assert result[0]._threshold == 5


# ---------------------------------------------------------------------------
# Conditional + tracker unit tests
# ---------------------------------------------------------------------------


def test_conditional_skips_below_threshold():
    """When tools <= threshold, selector is skipped."""
    mock_selector = MagicMock()
    cond = _ConditionalToolSelectorMiddleware(mock_selector, threshold=10)

    request = MagicMock()
    request.tools = [MagicMock() for _ in range(5)]
    handler = MagicMock()

    cond.wrap_model_call(request, handler)
    handler.assert_called_once_with(request)
    mock_selector.wrap_model_call.assert_not_called()


def test_conditional_runs_above_threshold():
    """When tools > threshold, selector runs."""
    mock_selector = MagicMock()
    cond = _ConditionalToolSelectorMiddleware(mock_selector, threshold=10)

    request = MagicMock()
    request.tools = [MagicMock() for _ in range(15)]
    handler = MagicMock()

    cond.wrap_model_call(request, handler)
    mock_selector.wrap_model_call.assert_called_once()
    handler.assert_not_called()


def test_selector_active_flag():
    """_selector_active flag is True during selection, False after."""
    import tyqa.middleware.tool_selector as ts_mod

    mock_selector = MagicMock()

    def fake_selector_call(request, handler):
        assert ts_mod._selector_active is True
        return handler(request)

    mock_selector.wrap_model_call.side_effect = fake_selector_call
    cond = _ConditionalToolSelectorMiddleware(mock_selector, threshold=5)

    request = MagicMock()
    request.tools = [MagicMock() for _ in range(10)]
    handler = MagicMock()

    cond.wrap_model_call(request, handler)
    assert ts_mod._selector_active is False


def test_tracker_captures_tools():
    """Tracker middleware captures tool names from request."""
    tracker = _ToolSelectionTrackerMiddleware()
    mock_tool1 = MagicMock()
    mock_tool1.name = "read_file"
    mock_tool2 = MagicMock()
    mock_tool2.name = "execute"

    request = MagicMock()
    request.tools = [mock_tool1, mock_tool2]
    handler = MagicMock()

    tracker.wrap_model_call(request, handler)
    handler.assert_called_once_with(request)

    import tyqa.middleware.tool_selector as ts_mod

    assert ts_mod._current_selected_tools == ["read_file", "execute"]


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------


@patch(
    "tyqa.middleware.create_tool_selector_middleware",
    side_effect=lambda *a, **kw: _patched_create(),
)
@patch("tyqa.agent_graph._ensure_chat_model")
@patch("tyqa.agent_graph._ensure_config")
def test_default_middleware_includes_tool_selector(mock_config, mock_model, mock_ts):
    mock_model.return_value = _mock_model()
    cfg = MagicMock()
    cfg.enable_ask_user = False
    cfg.auto_approve = False
    cfg.auxiliary_model = ""
    cfg.auxiliary_provider = ""
    mock_config.return_value = cfg

    from tyqa.agent_graph import _get_default_middleware

    mw = _get_default_middleware()
    type_names = [type(m).__name__ for m in mw]
    assert "_ConditionalToolSelectorMiddleware" in type_names
    assert "_ToolSelectionTrackerMiddleware" in type_names


@patch(
    "tyqa.middleware.create_tool_selector_middleware",
    side_effect=lambda *a, **kw: _patched_create(),
)
@patch("tyqa.agent_graph._ensure_chat_model")
@patch("tyqa.agent_graph._ensure_config")
def test_async_subagent_middleware_disables_stream_tracking(
    mock_config, mock_model, mock_ts
):
    mock_model.return_value = _mock_model()
    cfg = MagicMock()
    cfg.enable_ask_user = False
    cfg.auto_approve = False
    cfg.model_fallbacks = None
    cfg.auxiliary_model = ""
    cfg.auxiliary_provider = ""
    cfg.memory_profile_enabled = False
    cfg.memory_observations_enabled = False
    cfg.memory_workers_enabled = False
    mock_config.return_value = cfg

    from tyqa.agent_graph import _get_default_middleware

    _get_default_middleware(for_async_subagent=True)

    assert mock_ts.call_args.kwargs["track_stream_selection"] is False


@patch("tyqa.agent_graph._ensure_chat_model")
def test_subagent_no_tool_selector(mock_model):
    mock_model.return_value = _mock_model()

    from tyqa.agent_graph import _inject_subagent_middleware

    subs = [{"name": "test-agent"}]
    _inject_subagent_middleware(subs)

    type_names = [type(m).__name__ for m in subs[0]["middleware"]]
    assert "_ConditionalToolSelectorMiddleware" not in type_names


@patch(
    "tyqa.middleware.create_tool_selector_middleware",
    side_effect=lambda *a, **kw: _patched_create(),
)
@patch("tyqa.agent_graph._ensure_chat_model")
@patch("tyqa.agent_graph._ensure_config")
def test_tool_selector_ordering(mock_config, mock_model, mock_ts):
    """ToolSelector should come after ToolErrorHandler and before Memory."""
    mock_model.return_value = _mock_model()
    cfg = MagicMock()
    cfg.enable_ask_user = False
    cfg.auto_approve = False
    cfg.auxiliary_model = ""
    cfg.auxiliary_provider = ""
    mock_config.return_value = cfg

    from tyqa.agent_graph import _get_default_middleware

    mw = _get_default_middleware()
    type_names = [type(m).__name__ for m in mw]

    ts_idx = type_names.index("_ConditionalToolSelectorMiddleware")
    tracker_idx = type_names.index("_ToolSelectionTrackerMiddleware")
    te_idx = type_names.index("ToolErrorHandlerMiddleware")
    mem_idx = type_names.index("TYQAMemoryMiddleware")
    assert te_idx < ts_idx < tracker_idx < mem_idx
