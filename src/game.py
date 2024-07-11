from abc import ABC, abstractmethod

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from settings import settings


class Agent(ABC):
    def __init__(self, temperature: float = 0.7):
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo", openai_api_key=settings.OPENAI_API_KEY, temperature=temperature
        )
        self.history: list[HumanMessage | AIMessage] = []
        self.system_message = SystemMessage(content=self.system_prompt)

    @property
    @abstractmethod
    def system_prompt(self) -> str: ...

    def respond(self) -> str:
        response = self.llm([self.system_message] + self.history)
        self.history.append(AIMessage(content=response.content))
        return response.content

    def listen(self, feedback: str) -> None:
        self.history.append(HumanMessage(content=feedback))


class TopicCreator(Agent):
    @property
    def system_prompt(self) -> str:
        return """
        You are the host in a game of 20 questions. Your task is to think of an object or living thing as the "topic" of the game.

        Requirements for the topic:
        1. It should be a specific object or living thing, not a category or abstract concept.
        2. It should be something that most people would recognize.
        3. It should not be too obscure or too broad.
        4. It should be challenging but possible to guess within 20 yes-or-no questions."""

    def create_topic(self) -> str:
        self.listen(
            "Generate a suitable topic for the game. Return only the name of the object or living thing, nothing else."
        )
        return self.respond()


class QuestionAsker(Agent):
    @property
    def system_prompt(self) -> str:
        return """
        You are playing 20 questions. Based on previous questions and answers, propose a new yes/no question to ask that will help guess the topic.
        The topic is a specific object or living thing, not a category or abstract concept. Randomise your questions when possible.
        If you feel confident you know what the object or living thing is you should ask if it's what you think it is."""

    def ask_question(self) -> str:
        self.listen("Please ask a new yes/no question.")
        return self.respond()

    def receive_feedback(self, feedback: str) -> str:
        self.listen(feedback)
        return self.respond()


if __name__ == "__main__":
    # print(TopicCreator().create_topic())
    question_asker = QuestionAsker()
    print(question_asker.ask_question())
    question_asker.receive_feedback("No")
    print(question_asker.ask_question())
    print(question_asker.history)
