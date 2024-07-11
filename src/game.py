from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from settings import settings


class TopicCreator:
    def __init__(self):
        chat = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            openai_api_key=settings.OPENAI_API_KEY,
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


# Usage example
if __name__ == "__main__":
    creator = TopicCreator()
    topic = creator.create_topic()
    print(f"Generated topic: {topic}")
