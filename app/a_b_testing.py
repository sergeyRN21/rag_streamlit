from rag_core import ConstitutionRag
from evaluate_rag import RagEvaluator

rag_v1 = ConstitutionRag(k=3)
rag_chain_v1, retriever_v1 = rag_v1.create_rag_chain()

# Создаём RAG с k=5
rag_v2 = ConstitutionRag(k=5)
rag_chain_v2, retriever_v2 = rag_v2.create_rag_chain()

evaluator_v1 = RagEvaluator(rag_chain_v1, retriever_v1)
evaluator_v2 = RagEvaluator(rag_chain_v2, retriever_v2)

evaluator_v1.run_evaluation(
    dataset_id="b1df60af-0c6c-44eb-a0d3-09819dc434be",
    description="RAG_k3"
)

evaluator_v2.run_evaluation(
    dataset_id="b1df60af-0c6c-44eb-a0d3-09819dc434be",
    description="RAG_k5"
)

print("✅ A/B тестирование завершено!")