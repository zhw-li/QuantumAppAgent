"""``langgraph dev`` deployment surface.

Holds everything needed to run the TYQA agent ecosystem on a local
``langgraph dev`` subprocess:

- ``manager`` — subprocess lifecycle (auto-start, port management, cleanup).
- ``langgraph.json`` — graph manifest consumed by ``langgraph dev --config``.
- ``main_graph`` — re-export of the lazy-loaded ``tyqa_agent``.
- ``graphs`` — module-level bindings for every yaml-flagged async sub-agent
  (``async: true`` in ``tyqa/subagents/<name>.yaml``).

The graphs themselves are built by ``tyqa.subagents._factory.
build_async_subagent_graph`` from the canonical yaml definitions, so this
package only owns the *deployment* concern. Adding a new async sub-agent
takes three steps: flip the yaml flag, add a one-line binding in
``graphs.py``, and register it in ``langgraph.json``.
"""
