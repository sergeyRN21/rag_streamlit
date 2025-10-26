# evaluate_rag.py
import os
from dotenv import load_dotenv
from langsmith import evaluate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

load_dotenv()

# === 1. Твой RAG ===
from rag_core import create_rag_chain
rag_chain = create_rag_chain()

# === 2. Grader LLM (Gemini 2.0 Flash через OpenRouter) ===
class CorrectnessGrade(BaseModel):
    explanation: str = Field(..., description="Обоснование оценки")
    correct: bool = Field(..., description="True если ответ корректен")

grader_llm = ChatOpenAI(
    model="google/gemini-2.0-flash-001",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.0,
    max_tokens=512,
).with_structured_output(CorrectnessGrade, method="function_calling")

# === 3. Predict: example — dict в формате {"input": ..., "expected_output": ...} ===
def predict(example: dict) -> dict:
    # В evaluate() example — это плоский dict: {"input": "...", "expected_output": "..."}
    question = example["input"]  # ← Вот так правильно!
    result = rag_chain.invoke(question)

    if isinstance(result, str):
        answer = result
    elif isinstance(result, dict):
        answer = result.get("answer") or result.get("output") or str(result)
    else:
        answer = str(result)

    # Возвращаем с ключом "answer" — это имя, которое будем использовать в оценщике
    return {"answer": answer}

# === 4. Correctness evaluator: run — объект RunTree, example — объект Example ===
def correctness_evaluator(run, example) -> dict:
    # run.outputs — предсказание модели (из функции predict)
    prediction = run.outputs.get("answer", "")

    # example.outputs — эталонный ответ из датасета (внутреннее хранение LangSmith)
    # В CSV: "expected_output" → в LangSmith: example.outputs["expected_output"]
    reference = (example.outputs or {}).get("expected_output")

    if not reference:
        print(f"⚠️ ВНИМАНИЕ: reference пустой для example.inputs: {example.inputs}")  # ← Отладка
        return {
            "key": "correctness",
            "score": 0.0,
            "comment": "⚠️ No reference answer in dataset (expected_output not found)"
        }

    # example.inputs — вопрос из датасета
    question = (example.inputs or {}).get("input") or ""

    prompt = f"""You are a fair teacher grading a quiz.
QUESTION: {question}
GROUND TRUTH ANSWER: {reference}
STUDENT ANSWER: {prediction}

Grade based ONLY on factual correctness. It is OK if:
- The student uses different wording
- The student provides extra correct facts
- The answer is shorter or longer

Only mark as incorrect if:
- The answer contradicts the ground truth
- The answer contains false information
- The answer is completely unrelated

Respond with a JSON object containing:
- "explanation": a short reason
- "correct": true or false
"""

    try:
        response = grader_llm.invoke([{"role": "user", "content": prompt}])
        score = 1.0 if response.correct else 0.0
        comment = response.explanation
    except Exception as e:
        score = 0.0
        comment = f"⚠️ Evaluation failed: {str(e)}"
        print(f"❌ ОШИБКА в оценщике: {e}")  # ← Отладка

    return {
        "key": "correctness",
        "score": score,
        "comment": comment
    }

# === 5. Запуск ===
if __name__ == "__main__":
    evaluate(
        predict,
        data="b1df60af-0c6c-44eb-a0d3-09819dc434be",
        evaluators=[correctness_evaluator],
        description="Digital Lawyer — Correctness (Gemini 2.0 Flash via OpenRouter)",
        max_concurrency=1,
    )
    print("✅ Оценка завершена.")