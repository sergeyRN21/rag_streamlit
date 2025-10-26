
import os
from dotenv import load_dotenv
from langsmith import evaluate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

load_dotenv()

from rag_core import create_rag_chain, rag_chain_with_k5
from evaluate_rag import CorrectnessGrade, correctness_evaluator, groundedness_evaluator, relevance_evaluator, retrieval_relevance_evaluator

rag_chain, retriever = create_rag_chain()
rag_chain_5, retriever_5 = rag_chain_with_k5()

grader_llm = ChatOpenAI(
    model="google/gemini-2.0-flash-001",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.0,
    max_tokens=512,
).with_structured_output(CorrectnessGrade, method="function_calling")

def predict_v1(example: dict) -> dict:
    question = example["input"]

    docs = retriever.invoke(question)
    contexts = [doc.page_content for doc in docs]
    answer = rag_chain.invoke(question)

    return {
        "answer": answer,
        "retrieved_contexts": contexts
    }

def predict_v2(example: dict) -> dict:
    question = example["input"]

    docs = retriever_5.invoke(question)
    contexts = [doc.page_content for doc in docs]
    answer = rag_chain_5.invoke(question)

    return {
        "answer": answer,
        "retrieved_contexts": contexts
    }


if __name__ == "__main__":
     results_v1 = evaluate(
         predict_v1,
         data="b1df60af-0c6c-44eb-a0d3-09819dc434be",
         evaluators=[
             correctness_evaluator,
             groundedness_evaluator,
             relevance_evaluator,
             retrieval_relevance_evaluator
         ],
         experiment_prefix="RAG_k3",
         description="RAG с k=3",
         max_concurrency=1
     )

     results_v2 = evaluate(
         predict_v2,
         data="b1df60af-0c6c-44eb-a0d3-09819dc434be",
         evaluators=[
             correctness_evaluator,
             groundedness_evaluator,
             relevance_evaluator,
             retrieval_relevance_evaluator
         ],
         experiment_prefix="RAG_k5",
         description="RAG с k=5",
         max_concurrency=1
     )
     print("✅ A/B тестирование завершено!")