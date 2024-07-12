from typing import Literal

from pydantic import BaseModel, Field


class Question(BaseModel):
    question: str = Field(description="The yes/no question being asked")


class AnswerSchema(BaseModel):
    question: str = Field(description="The question that was asked")
    answer: Literal["yes", "no"] = Field(description="The yes/no answer to the question asked")
    topic_guessed: Literal["yes", "no"] = Field(description="Yes/no has the topic been guessed by name?")


class QuestionReview(BaseModel):
    good_question: bool = Field(description="Whether the proposed question is good or not")
    explanation: str = Field(description="The rationale behind the decision of the review")
    better_questions: list[str] = Field(description="A list of better questions to ask")


class GameResult(BaseModel):
    time_taken: float
    questions_asked: int
