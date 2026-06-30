"""Tests for the /evoskills command (InstallSkills)."""

from unittest.mock import AsyncMock, MagicMock, patch

from tests.conftest import run_async as _run


def _ctx(supports_interactive=True):
    from tyqa.commands.base import CommandContext

    ui = MagicMock()
    ui.supports_interactive = supports_interactive
    ui.wait_for_skill_browse = AsyncMock()
    return CommandContext(agent=None, thread_id="tid", ui=ui), ui


_INDEX = [
    {
        "name": "delivery-writing",
        "description": "author papers",
        "install_source": "repo@delivery-writing",
        "tags": ["writing"],
    },
    {
        "name": "application-intake",
        "description": "brainstorm ideas",
        "install_source": "repo@application-intake",
        "tags": ["core"],
    },
]


class TestInstallSkills:
    def test_picker_cancel_no_install(self):
        from tyqa.commands.implementation.skills import InstallSkills

        ctx, ui = _ctx()
        ui.wait_for_skill_browse.return_value = None  # cancelled
        with (
            patch(
                "tyqa.tools.skills_manager.fetch_remote_skill_index",
                return_value=_INDEX,
            ),
            patch(
                "tyqa.tools.skills_manager.install_skill",
            ) as install_mock,
        ):
            _run(InstallSkills().execute(ctx, []))
        install_mock.assert_not_called()
        msgs = [c.args[0] for c in ui.append_system.call_args_list]
        assert any("Browse cancelled" in m for m in msgs)

    def test_picker_returns_selections_installs_each(self):
        from tyqa.commands.implementation.skills import InstallSkills

        ctx, ui = _ctx()
        ui.wait_for_skill_browse.return_value = [
            "repo@delivery-writing",
            "repo@application-intake",
        ]
        with (
            patch(
                "tyqa.tools.skills_manager.fetch_remote_skill_index",
                return_value=_INDEX,
            ),
            patch(
                "tyqa.tools.skills_manager.install_skill",
                return_value={"success": True, "name": "x"},
            ) as install_mock,
        ):
            _run(InstallSkills().execute(ctx, []))
        assert install_mock.call_count == 2

    def test_channel_auto_install_on_tag(self):
        """Non-interactive UI + tag arg → auto-installs matching skills."""
        from tyqa.commands.implementation.skills import InstallSkills

        ctx, ui = _ctx(supports_interactive=False)
        with (
            patch(
                "tyqa.tools.skills_manager.fetch_remote_skill_index",
                return_value=_INDEX,
            ),
            patch(
                "tyqa.tools.skills_manager.install_skill",
                return_value={"success": True, "name": "x"},
            ) as install_mock,
        ):
            _run(InstallSkills().execute(ctx, ["core"]))
        # "core" matches application-intake only → 1 install, no picker call
        assert install_mock.call_count == 1
        ui.wait_for_skill_browse.assert_not_called()

    def test_fetch_failure_prints_error(self):
        from tyqa.commands.implementation.skills import InstallSkills

        ctx, ui = _ctx()
        with patch(
            "tyqa.tools.skills_manager.fetch_remote_skill_index",
            side_effect=RuntimeError("network fail"),
        ):
            _run(InstallSkills().execute(ctx, []))
        msgs = [c.args[0] for c in ui.append_system.call_args_list]
        assert any("Failed to fetch" in m for m in msgs)
