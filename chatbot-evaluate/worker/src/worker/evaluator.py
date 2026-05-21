from typing import List
from ragas.metrics.collections import Faithfulness, ContextUtilization, AnswerRelevancy
from ragas.llms import llm_factory
from ragas.embeddings import GoogleEmbeddings
from ragas.embeddings.base import embedding_factory

class Evaluator:

    def __init__(self, settings):

        if settings.provider == "google":    
            from google import genai
            client = genai.Client(api_key=settings.model_api_key)
            llm = llm_factory(
                settings.model_id,
                provider="google",
                temperature = settings.temperature,
                client=client
            )
            self.llm = llm
            self.embedding = embedding_factory("google", api_key = settings.model_api_key, model=settings.embed_model_id)

    async def evaluate(self,
            question: str,
            answer: str,
            context: List[str]
    ):

        faith_scorer = Faithfulness(self.llm)
        faith_result = await faith_scorer.ascore(
            user_input=question,
            response=answer,
            retrieved_contexts = context
        )
        faith_score = faith_result.value

        # utilsization_scorer = ContextUtilization(self.llm)
        # utilization_result = await utilsization_scorer.ascore(
        #     user_input=question,
        #     response=answer,
        #     retrieved_contexts = context
        # )
        # utilization_score = utilization_result.value
        # scorer = AnswerRelevancy(llm=llm, embeddings=embeddings)
        
        return {
            "relevancy": 0,
            "faithfulness": faith_score,
            "utilization":0
        }