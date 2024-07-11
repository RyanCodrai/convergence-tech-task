from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from settings import settings


class TopicCreator:
    def __init__(self, temperature: float = 0.7):
        chat = ChatOpenAI(
            model_name="gpt-3.5-turbo", openai_api_key=settings.OPENAI_API_KEY, temperature=temperature
        )
        prompt = ChatPromptTemplate.from_template(
            """You are the host in a game of 20 questions. Your task is to think of an object or living thing as the "topic" of the game.

            Requirements for the topic:
            1. It should be a specific object or living thing, not a category or abstract concept.
            2. It should be something that most people would recognize.
            3. It should not be too obscure or too broad.
            4. It should be challenging but possible to guess within 20 yes-or-no questions.

            Generate a suitable topic for the game. Return only the name of the object or living thing, nothing else."""
        )
        self.chain = prompt | chat | StrOutputParser()

    def create_topic(self):
        return self.chain.invoke({"input": ""})


class QuestionAsker:
    def __init__(self, temperature: float = 0.7):
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo", openai_api_key=settings.OPENAI_API_KEY, temperature=temperature
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are playing 20 questions. Based on previous questions and answers, propose a new yes/no question to ask that will help guess the topic. The topic is a specific object or living thing, not a category or abstract concept. ",
                ),
                ("user", "Here's the game history so far:\n{history}"),
                ("user", "Please ask a new yes/no question."),
            ]
        )
        self.memory = ConversationBufferMemory(input_key="history", memory_key="history")
        self.chain = prompt | llm

    def ask_question(self):
        # Use the memory's conversation history to generate the next question
        history = self.memory.load_memory_variables({})["history"]
        result = self.chain.invoke({"history": history})
        return result.content


if __name__ == "__main__":
    # print(TopicCreator().create_topic())
    print(QuestionAsker().ask_question())
