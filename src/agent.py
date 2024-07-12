from abc import ABC, abstractmethod
from typing import Optional, Union

from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import PydanticOutputParser
from langfuse import Langfuse
from langfuse.decorators import observe
from langfuse.openai import AsyncOpenAI
from pydantic import BaseModel
from tenacity import before_sleep_log, retry, stop_after_attempt

from src.models import AnswerSchema, Question, QuestionReview
from src.settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
langfuse = Langfuse(
    secret_key=settings.LANGFUSE_SECRET_KEY,
    public_key=settings.LANGFUSE_PUBLIC_KEY,
    host="https://cloud.langfuse.com",
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class Agent(ABC):
    def __init__(self, temperature: float = 0.7, api_key: Optional[str] = None):
        self.temperature = temperature
        self.history: list[dict] = []
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    @property
    @abstractmethod
    def system_prompt(self) -> str: ...

    async def generate_output(self, structured_response: Optional[BaseModel] = None) -> Union[str, BaseModel]:
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.history,
        ]

        if structured_response:
            parser = PydanticOutputParser(pydantic_object=structured_response)
            format_instructions = parser.get_format_instructions()
            messages.append({"role": "user", "content": format_instructions})

        response = (
            (
                await self.client.chat.completions.create(
                    model="gpt-4o", temperature=self.temperature, messages=messages
                )
            )
            .choices[0]
            .message.content
        )

        self.history.append({"role": "assistant", "content": response})

        if structured_response:
            return parser.parse(response)
        return response

    def receive_input(self, input_text: str) -> None:
        self.history.append({"role": "user", "content": input_text})


class TopicCreator(Agent):
    @property
    def system_prompt(self) -> str:
        return """
        You are the host in a game of 20 questions. Your task is to think of an object or living thing as the "topic" of the game.

        Requirements for the topic:
        1. It should be a specific object or living thing, not a category or abstract concept.
        2. It should be something that most people would recognise.
        3. It should not be too obscure or too broad.
        4. It should be challenging but possible to guess within 20 yes-or-no questions.
        5. It should be random."""

    @observe()
    @retry(
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_log(logger, logging.ERROR),
    )
    async def create_topic(self) -> str:
        self.receive_input("Generate a suitable topic for the game. Return only the name, nothing else.")
        topic = await self.generate_output()
        logger.info(f"Topic created: {topic}")
        return topic


class QuestionAnswerer(Agent):
    def __init__(self, temperature: float = 0.7):
        super().__init__(temperature)
        loop = asyncio.get_event_loop()
        self.game_topic_future = asyncio.ensure_future(TopicCreator().create_topic(), loop=loop)

    @property
    def system_prompt(self) -> str:
        return """
        You are answering yes/no questions in a game of 20 questions.
        NEVER share the topic of the game directly.
        DO let the player know if they have guessed the topic correctly."""

    @observe()
    @retry(
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_log(logger, logging.ERROR),
    )
    async def answer_question(self, question: str) -> AnswerSchema:
        topic = await self.game_topic_future
        self.receive_input(f"The topic is '{topic}'.")
        self.receive_input(question)
        answer = await self.generate_output(AnswerSchema)
        logger.info(f"Question answered: {question} -> {answer.answer}")
        return answer


class QuestionPlanner(Agent):
    def __init__(self, temperature: float = 0.7):
        super().__init__(temperature)

    @property
    def system_prompt(self) -> str:
        return """
        ### Objective:
        You are a Question Asker in a game of 20 questions. Your task is to plan and ask questions that will help identify the topic chosen by the Topic Creator. You will formulate questions and submit them to the Question Reviewer to ensure they are strategic, clear, and effective.

        ### Instructions:
        1. **Understand the Context:** Review the current state of the game, including previous questions and answers.
        2. **Formulate Questions:** Based on the information available, plan clear and concise questions that will help narrow down the topic.
        3. **Submit for Review:** Submit your proposed questions to the Question Reviewer for feedback.
        4. **Incorporate Feedback:** Based on the review, refine your questions to improve their effectiveness, clarity, and relevance.
        5. **Ask the Question:** Once approved by the Question Reviewer, ask the question to the Question Answerer.
        6. **Record Responses:** Keep track of the responses from the Question Answerer and use this information to guide your subsequent questions.

        ### Considerations:
        - **Effectiveness:** Ensure each question helps in significantly narrowing down the topic.
        - **Clarity:** Formulate questions that are clear and easy to understand.
        - **Relevance:** Ensure the questions are relevant to the topic and the information gathered so far.
        - **Avoid Redundancy:** Avoid questions that have already been effectively answered indirectly."""

    @observe()
    @retry(
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_log(logger, logging.ERROR),
    )
    async def ask_question(self, questions_asked: int) -> Question:
        self.receive_input(f"Questions asked so far: {questions_asked}.")
        self.receive_input("Please ask a new yes/no question.")
        question = await self.generate_output(Question)
        logger.info(f"Question created: {question.question}")
        return question

    def receive_feedback(self, question_review: BaseModel) -> None:
        self.receive_input(str(question_review))


class QuestionReviewer(Agent):
    @property
    def system_prompt(self) -> str:
        return """
        ### Objective:
        You are a Question Reviewer. Your task is to review the questions proposed by the Question Asker and determine whether each question is good to ask. Your feedback should include a clear decision and reasoning to ensure each question effectively contributes to narrowing down the topic.

        ### Instructions:
        1. **Understand the Context:** Review the current state of the game, including the topic and previous questions and answers.
        2. **Review Proposed Question:** Examine the question proposed by the Question Asker.
        3. **Decision Making:** Decide whether the proposed question is a good one to ask.
        4. **Provide Feedback:** Explain your decision with clear reasoning, focusing on the question's effectiveness, clarity, and relevance.
        5. **Approval or Rejection:** Clearly state whether the question is approved or rejected, and if rejected, suggest improvements or alternatives.

        ### Considerations:
        - **Effectiveness:** Does the question help in significantly narrowing down the topic?
        - **Clarity:** Is the question clear and easy to understand?
        - **Relevance:** Is the question relevant to the topic and the information gathered so far?
        - **Redundancy:** Avoid questions that have already been answered or are redundant."""

    @observe()
    @retry(
        stop=stop_after_attempt(3),
        before_sleep=before_sleep_log(logger, logging.ERROR),
    )
    async def review_question(self, question: str, questions_asked: int) -> QuestionReview:
        self.receive_input(f"Questions asked so far: {questions_asked}")
        self.receive_input(f"Question for review: {question}")
        review = await self.generate_output(QuestionReview)
        logger.info(f"Question reviewed: {question} -> Approved: {review.good_question}")
        return review

    def receive_feedback(self, question_review: BaseModel) -> None:
        self.receive_input(str(question_review))
