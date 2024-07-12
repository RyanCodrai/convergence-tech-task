import asyncio
import logging
import time

from src.agent import QuestionAnswerer, QuestionPlanner, QuestionReviewer
from src.models import GameResult, Question
from src.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class GameCoordinator:
    def __init__(self):
        self.question_answerer = QuestionAnswerer()
        self.question_planner = QuestionPlanner()
        self.question_reviewer = QuestionReviewer()
        self.questions_asked = 0

    async def plan_question(self) -> Question:
        for _ in range(settings.PLANNER_REVIEW_COUNT):
            question = await self.question_planner.ask_question(self.questions_asked)
            feedback = await self.question_reviewer.review_question(question.question, self.questions_asked)
            if feedback.good_question:
                break
        self.questions_asked += 1
        return question

    async def start_game(self) -> GameResult:
        logger.info(f"Beginning 20 questions with topic {await self.question_answerer.game_topic_future}")
        start_time = time.time()
        while self.questions_asked < 20:
            question = await self.plan_question()
            answer = await self.question_answerer.answer_question(question.question)

            if answer.topic_guessed == "yes":
                logger.info(f"Topic found in {self.questions_asked} questions.")
                break

            self.question_planner.receive_feedback(answer)

        result = GameResult(time_taken=time.time() - start_time, questions_asked=self.questions_asked)
        logger.info(f"Game ended. {str(result)}")
        return result


async def run_game_concurrent(semaphore: asyncio.Semaphore):
    async with semaphore:
        game = GameCoordinator()
        await game.start_game()


async def main():
    semaphore = asyncio.Semaphore(settings.CONCURRENT_GAMES)  # Limit to 3 concurrent games
    games: list[asyncio.Task] = []
    for _ in range(settings.TOTAL_GAMES):  # Queue up 10 games
        games.append(asyncio.create_task(run_game_concurrent(semaphore)))
    await asyncio.gather(*games)  # Run all games


if __name__ == "__main__":
    asyncio.run(main())
