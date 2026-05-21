import asyncio
import json
from logging import Logger
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.prompts import RichPromptTemplate

from typing import Any
from models import get_llm, LLM
from env import (
    get_task_settings,
    TaskSettings,
    get_global_settings,
    GlobalSettings,
    get_nosql_settings,
    NOSQLSettings,
)

from dos_utility.database.nosql import get_nosql_client_ctx, QueryResult, KeyCondition, ConditionOperator
from dos_utility.utils.logger import get_logger

async def process_task(body: bytes) -> None:
    """Process a task with the given body.

    Args:
        body (bytes): The body of the task to be processed.
    """

    settings: GlobalSettings = get_global_settings()
    task_settings: TaskSettings = get_task_settings()
    nosql_settings: NOSQLSettings = get_nosql_settings()
    logger: Logger = get_logger(name=__name__, level=settings.log_level)

    llm: LLM = get_llm(
        provider = task_settings.provider,
        model_id = task_settings.model_id,
        temperature = task_settings.temperature,
        max_tokens = task_settings.max_tokens,
        api_key = task_settings.model_api_key,
    )

    logger.debug("Initializing document loader, parser, and embedder...")

    converted_data: Any = json.loads(body.decode("utf-8"))
    session_id = converted_data['sessionId']
    message_id = converted_data['messageId']

    async with  get_nosql_client_ctx() as nosql_client:
        query_result: QueryResult = await nosql_client.query(
                table_name= nosql_settings.query_tablename,
                key_conditions=[
                    KeyCondition(
                        field="sessionId", operator=ConditionOperator.EQ, value=session_id
                    )
                ],
            )
        chat_session = query_result.items

    chat_session = sorted(query_result.items, key = lambda x: x['createdAt'])
    if len(chat_session) > 1:
        history = []
        for chat_message in chat_session:
            if chat_message["id"] == message_id:
                message_to_evaluate = chat_message
                break
            else:
                history += [
                    ChatMessage(role=MessageRole.USER, content= chat_message['question']),
                    ChatMessage(role=MessageRole.ASSISTANT, content=chat_message['answer']),
                ]
        
        ### domanda sintetica
        prompt_template = """
        Il tuo compito è scrivere una domanda contestualizza considerando i messaggi che sono stati precedentemente scambiati.
        
        La domanda fatta è la seguente:
        {{question}}

        I messaggi scambiati sono:
        {{history}}

        Domanda contestualizzata:
""" 
        synthesis_prompt = RichPromptTemplate(prompt_template)
        contextualized_question = llm.acomplete(synthesis_prompt.format(
            question = message_to_evaluate['question'],
            history = history)
            )
        question_to_evaluate = contextualized_question.text.strip()
        
        print("Contextualized question:", question_to_evaluate)
    else:
        question_to_evaluate = chat_session[0]['question']
    
    ### JUDGE
        


            
    
