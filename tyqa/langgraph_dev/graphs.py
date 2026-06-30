"""Deployed graphs for all yaml-flagged async sub-agents.

One module-level binding per ``async: true`` entry in
``tyqa/subagents/<name>.yaml``. Each binding is a graph compiled by
``build_async_subagent_graph`` (which reads the yaml, wires tools/skills/
backend/middleware identical to the in-process sync version, and returns a
runnable langgraph).

To add a new async sub-agent:

  1. Set ``async: true`` in ``tyqa/subagents/<name>.yaml``.
  2. Add a one-line binding here::

         <snake_name>_agent = build_async_subagent_graph("<name>")

  3. Register it in ``tyqa/langgraph_dev/langgraph.json``::

         "<name>": "tyqa.langgraph_dev.graphs:<snake_name>_agent"

The deployed main agent (``tyqa_agent``) lives in ``main_graph.py``
because it follows a different mechanism (re-exporting a lazily-constructed
attribute), not the yaml-driven factory.
"""

from tyqa.middleware.memory_lifecycle import (
    MemoryLifecycleRole,
    build_memory_worker_graph,
)
from tyqa.subagents._factory import build_async_subagent_graph

writing_agent = build_async_subagent_graph("writing-agent")
data_analysis_agent = build_async_subagent_graph("data-analysis-agent")
evomemory_subagent_worker = build_memory_worker_graph(MemoryLifecycleRole.SUBAGENT)
evomemory_turn_worker = build_memory_worker_graph(MemoryLifecycleRole.TURN)
