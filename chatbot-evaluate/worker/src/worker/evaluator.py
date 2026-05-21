from typing import List
from ragas.metrics.collections import Faithfulness, ContextUtilization, AnswerRelevancy

class Evaluator:

    def __init__(self, llm, embedding):
        self.llm = llm
        self.embedding = embedding

    def evaluate(
            question: str,
            answer: str,
            context: List[str]
    ):
        
        return {
            "relevancy": 0,
            "faithfulness":0,
            "utilization":0
        }