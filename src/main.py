"""Backward-compatibility module for legacy scripts and imports.

Redirects imports to the modularized docuagent package:
- agent_init -> docuagent.ui.cache.get_cached_agent / docuagent.agent.factory.create_rag_agent
- eval_trace -> docuagent.observability.metrics.eval_trace
- config -> docuagent.observability.langfuse.get_agent_config()
"""

from docuagent.agent.factory import create_rag_agent
from docuagent.ui.cache import get_cached_agent as agent_init
from docuagent.observability.metrics import eval_trace
from docuagent.observability.langfuse import get_agent_config, context_manager

config = get_agent_config()

__all__ = [
    "agent_init",
    "create_rag_agent",
    "eval_trace",
    "config",
    "context_manager",
]
