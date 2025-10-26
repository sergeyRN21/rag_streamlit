# evaluate_rag.py
import os
from dotenv import load_dotenv
from langsmith import evaluate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

load_dotenv()

class CorrectnessGrade(BaseModel):
    explanation: str = Field(..., description="Обоснование оценки")
    correct: bool = Field(..., description="True если ответ корректен")

class RagEvaluator:
    def __init__(self, rag_chain, retriever):
        self.rag_chain = rag_chain
        self.retriever = retriever
        self.grader_llm = ChatOpenAI(
            model="google/gemini-2.0-flash-001",
            base_url="https://openrouter.ai/api/v1",  # ✅ Убран лишний пробел
            api_key=os.getenv("OPENROUTER_API_KEY"),
            temperature=0.0,
            max_tokens=512,
        ).with_structured_output(CorrectnessGrade, method="function_calling")

    def predict(self, example: dict) -> dict:
        question = example["input"]
        docs = self.retriever.invoke(question)
        contexts = [doc.page_content for doc in docs]
        answer = self.rag_chain.invoke(question)
        return {
            "answer": answer,
            "retrieved_contexts": contexts
        }

    def correctness_evaluator(self, run, example) -> dict:
        prediction = run.outputs.get("answer", "")
        reference = (example.outputs or {}).get("expected_output")

        if not reference:
            print(f"⚠️ ВНИМАНИЕ: reference пустой для example.inputs: {example.inputs}")
            return {
                "key": "correctness",
                "score": 0.0,
                "comment": "⚠️ No reference answer in dataset (expected_output not found)"
            }

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
            response = self.grader_llm.invoke([{"role": "user", "content": prompt}])
            score = 1.0 if response.correct else 0.0
            comment = response.explanation
        except Exception as e:
            score = 0.0
            comment = f"⚠️ Evaluation failed: {str(e)}"
            print(f"❌ ОШИБКА в correctness: {e}")

        return {
            "key": "correctness",
            "score": score,
            "comment": comment
        }

    def groundedness_evaluator(self, run, example) -> dict:
        prediction = run.outputs.get("answer", "")
        contexts = run.outputs.get("retrieved_contexts", [])

        if not contexts:
            return {
                "key": "groundedness",
                "score": 0.0,
                "comment": "⚠️ No retrieved contexts provided for groundedness check"
            }

        context_str = "\n\n".join(contexts)

        prompt = f"""You are a teacher checking if a student's answer is grounded in the provided facts.
CONTEXT: {context_str}
STUDENT ANSWER: {prediction}

Check if the STUDENT ANSWER is supported by the CONTEXT. Answer "True" if the answer is supported by the facts, "False" if it contains hallucinated or unsupported information.

Respond with a JSON object containing:
- "explanation": a short reason
- "correct": true or false
"""

        try:
            response = self.grader_llm.invoke([{"role": "user", "content": prompt}])
            score = 1.0 if response.correct else 0.0
            comment = response.explanation
        except Exception as e:
            score = 0.0
            comment = f"⚠️ Evaluation failed: {str(e)}"
            print(f"❌ ОШИБКА в groundedness: {e}")

        return {
            "key": "groundedness",
            "score": score,
            "comment": comment
        }

    def relevance_evaluator(self, run, example) -> dict:
        question = (example.inputs or {}).get("input") or ""
        prediction = run.outputs.get("answer", "")

        if not question:
            return {
                "key": "relevance",
                "score": 0.0,
                "comment": "⚠️ No question provided"
            }

        prompt = f"""You are a teacher checking if a student's answer is relevant to the question.
QUESTION: {question}
STUDENT ANSWER: {prediction}

Check if the STUDENT ANSWER is relevant to the QUESTION and helps answer it. Answer "True" if it is, "False" if it is not.

Respond with a JSON object containing:
- "explanation": a short reason
- "correct": true or false
"""

        try:
            response = self.grader_llm.invoke([{"role": "user", "content": prompt}])
            score = 1.0 if response.correct else 0.0
            comment = response.explanation
        except Exception as e:
            score = 0.0
            comment = f"⚠️ Evaluation failed: {str(e)}"
            print(f"❌ ОШИБКА в relevance: {e}")

        return {
            "key": "relevance",
            "score": score,
            "comment": comment
        }

    def retrieval_relevance_evaluator(self, run, example) -> dict:
        question = (example.inputs or {}).get("input") or ""
        contexts = run.outputs.get("retrieved_contexts", [])

        if not contexts:
            return {
                "key": "retrieval_relevance",
                "score": 0.0,
                "comment": "⚠️ No retrieved contexts provided"
            }

        context_str = "\n\n".join(contexts)

        prompt = f"""You are a teacher checking if the retrieved documents are relevant to the question.
QUESTION: {question}
RETRIEVED DOCUMENTS: {context_str}

Check if the RETRIEVED DOCUMENTS are relevant to the QUESTION. Answer "True" if they contain information related to the question, "False" if they are completely unrelated.

Respond with a JSON object containing:
- "explanation": a short reason
- "correct": true or false
"""

        try:
            response = self.grader_llm.invoke([{"role": "user", "content": prompt}])
            score = 1.0 if response.correct else 0.0
            comment = response.explanation
        except Exception as e:
            score = 0.0
            comment = f"⚠️ Evaluation failed: {str(e)}"
            print(f"❌ ОШИБКА в retrieval_relevance: {e}")

        return {
            "key": "retrieval_relevance",
            "score": score,
            "comment": comment
        }

    def run_evaluation(self, dataset_id: str, description: str = "RAG Evaluation"):
        evaluators = [
            self.correctness_evaluator,
            self.groundedness_evaluator,
            self.relevance_evaluator,
            self.retrieval_relevance_evaluator
        ]
        evaluate(
            self.predict,
            data=dataset_id,
            evaluators=evaluators,
            description=description,
            max_concurrency=1,
        )
        print("✅ Оценка завершена.")