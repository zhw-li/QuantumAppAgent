"""Deployed graph entry for the main TYQA agent.

The main ``tyqa_agent`` is exposed via ``__getattr__`` lazy loading
in ``tyqa/tyqa.py`` so it doesn't construct on plain
``import tyqa``. ``langgraph dev`` 's symbol resolver inspects
module attributes directly and doesn't trigger ``__getattr__``, so we
re-export here to make it visible.
"""

from tyqa.agent_graph import tyqa_agent

__all__ = ["tyqa_agent"]
