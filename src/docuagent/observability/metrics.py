"""Ragas metrics evaluation and Langfuse score tracking."""

import sys
from typing import List, Dict, Any, Optional, Union

# ---------------------------------------------------------------------------
# Compatibility Shim for Ragas Issue #2745 (Broken ChatVertexAI / VertexAI imports)
# In langchain-community >= 0.4, VertexAI classes moved to langchain-google-vertexai.
# Unpatched Ragas on PyPI (e.g. Streamlit Cloud) imports from the old paths.
# We map the old paths in sys.modules to langchain_google_vertexai at runtime.
# ---------------------------------------------------------------------------
if "langchain_community.chat_models.vertexai" not in sys.modules:
    try:
        import langchain_google_vertexai

        sys.modules["langchain_community.chat_models.vertexai"] = langchain_google_vertexai
        sys.modules["langchain_community.llms.vertexai"] = langchain_google_vertexai
        try:
            import langchain_community.llms

            langchain_community.llms.VertexAI = langchain_google_vertexai.VertexAI
        except (ImportError, AttributeError):
            pass
    except ImportError:
        pass

from ragas.metrics import (
    Faithfulness,
    ResponseRelevancy,
    LLMContextPrecisionWithoutReference,
)
from ragas.run_config import RunConfig
from ragas.metrics.base import MetricWithLLM, MetricWithEmbeddings
from ragas.dataset_schema import SingleTurnSample

# ---------------------------------------------------------------------------
# Compatibility Patch for Ragas LLM JSON Parsing with Markdown Code Fences
# Raw PyPI Ragas crashes when LLMs return ```json ... ``` inside PydanticPrompt.
# We monkeypatch PydanticPrompt.generate_multiple to wrap output_model validation.
# ---------------------------------------------------------------------------
try:
    import ragas.prompt.pydantic_prompt as pp
    from ragas.prompt.utils import extract_json

    _orig_generate_multiple = pp.PydanticPrompt.generate_multiple

    async def _patched_generate_multiple(self, *args, **kwargs):
        if hasattr(self, "output_model") and hasattr(self.output_model, "model_validate_json"):
            model_cls = self.output_model
            if not getattr(model_cls, "_ragas_extract_json_patched", False):
                _orig_validate = model_cls.model_validate_json

                def _clean_validate(json_data, *a, **k):
                    if isinstance(json_data, str):
                        json_data = extract_json(json_data)
                    return _orig_validate(json_data, *a, **k)

                model_cls.model_validate_json = _clean_validate
                model_cls._ragas_extract_json_patched = True
        return await _orig_generate_multiple(self, *args, **kwargs)

    pp.PydanticPrompt.generate_multiple = _patched_generate_multiple
except (ImportError, AttributeError):
    pass

from docuagent.observability.langfuse import get_langfuse_client, context_manager


# Default evaluation metrics
default_metrics = [
    Faithfulness(),
    ResponseRelevancy(),
    LLMContextPrecisionWithoutReference(),
]


def init_ragas_metrics(
    metrics_list: Optional[List[Any]] = None,
    llm: Any = None,
    embedding: Any = None,
) -> List[Any]:
    """Initialize Ragas metrics with LLM and embedding instances."""
    active_metrics = metrics_list or default_metrics
    for metric in active_metrics:
        if isinstance(metric, MetricWithLLM) and llm is not None:
            metric.llm = llm
        if isinstance(metric, MetricWithEmbeddings) and embedding is not None:
            metric.embeddings = embedding
        run_config = RunConfig()
        metric.init(run_config)
    return active_metrics


async def score_with_ragas(
    query: str,
    chunks: Union[str, List[str]],
    answer: str,
    metrics_list: Optional[List[Any]] = None,
) -> Dict[str, float]:
    """Calculate Ragas scores for a single turn (query, retrieved context, response)."""
    active_metrics = metrics_list or default_metrics
    scores: Dict[str, float] = {}

    # Ensure chunks is always a list of strings
    if isinstance(chunks, str):
        normalized_chunks = [chunks] if chunks.strip() else []
    elif chunks is None:
        normalized_chunks = []
    else:
        normalized_chunks = list(chunks)

    for m in active_metrics:
        sample = SingleTurnSample(
            user_input=query,
            retrieved_contexts=normalized_chunks,
            response=answer,
        )
        scores[m.name] = await m.single_turn_ascore(sample)

    return scores


async def eval_trace(
    question: str,
    answer: str,
    context: Optional[List[str]] = None,
    metrics_list: Optional[List[Any]] = None,
) -> Dict[str, float]:
    """Create a Langfuse observation trace, evaluate with Ragas, and attach scores."""
    client = get_langfuse_client()
    active_metrics = metrics_list or default_metrics
    contexts = context if context is not None else context_manager.get_all()

    with client.start_as_current_observation(as_type="span", name="rag") as trace:
        trace_id = trace.trace_id

        # Retrieval observation
        with trace.start_as_current_observation(
            name="retrieval",
            input={"question": question},
            output={"contexts": contexts},
        ):
            pass

        # Generation observation
        with trace.start_as_current_observation(
            name="generation",
            input={"question": question, "contexts": contexts},
            output={"answer": answer},
        ):
            pass

        # Calculate scores
        ragas_scores = await score_with_ragas(question, contexts, answer, active_metrics)

    # Attach score records to the Langfuse trace
    for m in active_metrics:
        if m.name in ragas_scores:
            client.create_score(
                name=m.name,
                value=float(ragas_scores[m.name]),
                trace_id=trace_id,
            )

    # Reset collected context for next query
    context_manager.clear()
    return ragas_scores
