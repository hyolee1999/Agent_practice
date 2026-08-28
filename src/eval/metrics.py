# import metrics
from ragas.metrics import (
    Faithfulness,
    ResponseRelevancy,
    LLMContextPrecisionWithoutReference,
)
from ragas.run_config import RunConfig
from ragas.metrics.base import MetricWithLLM, MetricWithEmbeddings
from ragas.dataset_schema import SingleTurnSample

# metrics you chose
metrics = [
    Faithfulness(),
    ResponseRelevancy(),
    LLMContextPrecisionWithoutReference(),
]


# util function to init Ragas Metrics
def init_ragas_metrics(metrics, llm, embedding):
    for metric in metrics:
        if isinstance(metric, MetricWithLLM):
            metric.llm = llm
        if isinstance(metric, MetricWithEmbeddings):
            metric.embeddings = embedding
        run_config = RunConfig()
        metric.init(run_config)


async def score_with_ragas(query, chunks, answer):
    scores = {}
    # Ensure chunks is always a list
    if isinstance(chunks, str):
        chunks = [chunks] if chunks else []
    for m in metrics:
        sample = SingleTurnSample(
            user_input=query,
            retrieved_contexts=chunks,
            response=answer,
        )
        print(f"calculating {m.name}")
        scores[m.name] = await m.single_turn_ascore(sample)
    return scores

