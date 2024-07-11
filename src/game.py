from abc import ABC, abstractmethod

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from settings import settings
from tenacity import retry, stop_after_attempt, wait_fixed


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


class QuestionAnswerer(Agent):
    def __init__(self, temperature: float = 0.7):
        super().__init__(temperature)
        game_topic = TopicCreator().create_topic()
        self.listen(f"The topic is '{game_topic}'.")

    @property
    def system_prompt(self) -> str:
        return """
        You are answering questions in a game of 20 questions.
        Based on the current question, provide only a 'yes' or 'no' answer in lowercase.
        Never share the topic of the game directly."""

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def answer_question(self, quesiton: str) -> str:
        self.listen(quesiton)
        answer = self.respond()
        if answer not in {"yes", "no"}:
            self.listen("Please only answer with 'yes' or 'no'")
            raise ValueError(f"Answer '{answer}' provided by QuestionAnswerer was not a yes or no answer.")
        return answer


class QuestionAsker(Agent):
    @property
    def system_prompt(self) -> str:
        return """
        You are playing 20 questions. Based on previous questions and answers, propose a new yes/no question to ask that will help guess the topic.
        The topic is a specific object or living thing, not a category or abstract concept. Randomize your questions when possible.
        If you feel confident you know what the object or living thing is you should ask if it's what you think it is."""

    def ask_question(self) -> str:
        self.listen("Please ask a new yes/no question.")
        return self.respond()

    def capture_feedback(self, feedback: str) -> None:
        self.listen(feedback)


class QuestionPlanner(Agent):
    @property
    def system_prompt(self) -> str:
        return """
        You are helping to plan the next question in a game of 20 questions. Based on the current topic and the history of questions and answers, refine or propose a new question."""

    def propose_question(self) -> str:
        self.listen("Propose or refine a new question based on the current topic and history.")
        return self.respond()


# class GameCoordinator:
#     def __init__(self):
#         self.topic_creator = TopicCreator()
#         self.question_asker = QuestionAsker()
#         self.question_planner = QuestionPlanner()
#         self.question_answerer = QuestionAnswerer()
#         self.history = []

#     def start_game(self):
#         topic = self.topic_creator.create_topic()
#         print(f"Topic created: {topic}")
#         for _ in range(20):
#             question = self.question_planner.propose_question()
#             print(f"Proposed question: {question}")
#             refined_question = self.question_asker.ask_question()
#             print(f"Refined question: {refined_question}")
#             answer = self.question_answerer.answer_question()
#             print(f"Answer: {answer}")
#             self.history.append((refined_question, answer))
#             if answer.lower() == "yes" and "correct" in refined_question.lower():
#                 print("Correct guess!")
#                 break
#         else:
#             print("20 questions asked. Game over.")


if __name__ == "__main__":
    # game_coordinator = GameCoordinator()
    # game_coordinator.start_game()

    print(QuestionAnswerer().answer_question("Is it something that can be found indoors?"))
