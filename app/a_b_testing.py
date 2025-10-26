from rag_core import create_rag_chain, rag_chain_with_k5
from evaluate_metrics import RagEvaluator

evaluator_v1 = RagEvaluator(*create_rag_chain())
evaluator_v2 = RagEvaluator(*rag_chain_with_k5())

evaluator_v1.run_evaluation(
    dataset_id="b1df60af-0c6c-44eb-a0d3-09819dc434be",
    description="RAG_k3"
)

evaluator_v2.run_evaluation(
    dataset_id="b1df60af-0c6c-44eb-a0d3-09819dc434be",
    description="RAG_k5"
)