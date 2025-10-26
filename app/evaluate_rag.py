# evaluate_rag.py
import os
from dotenv import load_dotenv
from langsmith import evaluate
from langsmith.evaluation import EvaluationResult
from rag_core import create_rag_chain

load_dotenv()

# Создаём цепочку ОДИН РАЗ
rag_chain = create_rag_chain()  # ← вне функции!

def predict(example):
    question = example["input_1"]
    answer = rag_chain.invoke(question)  # ← используем готовую цепочку
    return {"output": answer}

def faithfulness_evaluator(run, example):
    return EvaluationResult(key="faithfulness", score=None)

def answer_correctness_evaluator(run, example):
    return EvaluationResult(key="answer_correctness", score=None)

if __name__ == "__main__":
    evaluate(
        predict,
        data="96d6308d-394b-4fcf-92e2-962044656330",
        evaluators=[
            faithfulness_evaluator,
            answer_correctness_evaluator,
        ],
        description="Digital Lawyer — Cached Chain",
        max_concurrency=3,  # начни с 1 для отладки
    )
    print("✅ Оценка завершена.")