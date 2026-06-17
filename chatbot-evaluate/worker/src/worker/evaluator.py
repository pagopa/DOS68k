from typing import List
import os
import instructor
from ragas.metrics.collections import Faithfulness, ContextUtilization, AnswerRelevancy
from ragas.llms import InstructorLLM
from ragas.embeddings.base import embedding_factory


class Evaluator:
    def __init__(self, settings):

        if settings.provider == "google":
            from google import genai
            os.environ["GOOGLE_API_KEY"] = settings.model_api_key
            client = genai.Client(api_key=settings.model_api_key)
            async_instructor = instructor.from_genai(client, use_async=True)
            self.llm = InstructorLLM(
                client=async_instructor,
                model=settings.model_id,
                provider="google",
                temperature=settings.temperature,
            )
            self.embedding = embedding_factory(
                "google", 
                client = client, 
                model=settings.embed_model_id
            )

    async def evaluate(self, question: str, answer: str, context: List[str]):

        faith_scorer = Faithfulness(self.llm)
        utilsization_scorer = ContextUtilization(self.llm)

        faith_result = await faith_scorer.ascore(
            user_input=question, response=answer, retrieved_contexts=context
        )
        faith_score = faith_result.value

        utilization_result = await utilsization_scorer.ascore(
            user_input=question,
            response=answer,
            retrieved_contexts = context
        )
        utilization_score = utilization_result.value

        relevancy_scorer = AnswerRelevancy(llm=self.llm, 
                                           embeddings=self.embedding)
        relevancy_result = await relevancy_scorer.ascore(
            user_input = question,
            response = answer
        )
        relevancy_score = relevancy_result.value

        return {"relevancy": relevancy_score, "faithfulness": faith_score, "utilization": utilization_score}
