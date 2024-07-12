from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent import QuestionAnswerer, QuestionPlanner, QuestionReviewer, TopicCreator


@pytest.mark.asyncio
@patch("src.agent.AsyncOpenAI")
async def test_topic_creator(MockAsyncOpenAI):
    # Create a mock for the response to mimic the actual return structure
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="A cat"))]

    # Mock the client
    mock_client = MockAsyncOpenAI.return_value
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    # Create the agent and test
    agent = TopicCreator()
    result = await agent.create_topic()
    assert result == "A cat"


@pytest.mark.asyncio
@patch("src.agent.AsyncOpenAI")
async def test_question_answerer(MockAsyncOpenAI):
    # Create a mock for the response to mimic the actual return structure
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content='{"question": "Is it an animal?", "answer": "yes", "topic_guessed": "yes"}'
            )
        )
    ]

    # Mock the client
    mock_client = MockAsyncOpenAI.return_value
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    # Create the agent and test
    agent = QuestionAnswerer()
    result = await agent.answer_question("Is it an animal?")
    assert result.answer == "yes"


@pytest.mark.asyncio
@patch("src.agent.AsyncOpenAI")
async def test_question_planner(MockAsyncOpenAI):
    # Create a mock for the response to mimic the actual return structure
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content='{"question": "Is it a mammal?"}'))]

    # Mock the client
    mock_client = MockAsyncOpenAI.return_value
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    # Create the agent and test
    agent = QuestionPlanner()
    result = await agent.ask_question(0)
    assert result.question == "Is it a mammal?"


@pytest.mark.asyncio
@patch("src.agent.AsyncOpenAI")
async def test_question_reviewer(MockAsyncOpenAI):
    # Create a mock for the response to mimic the actual return structure
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content='{"good_question": true, "explanation": "Clear and relevant", "better_questions": ["Is it bigger than a breadbox?"]}'
            )
        )
    ]

    # Mock the client
    mock_client = MockAsyncOpenAI.return_value
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    # Create the agent and test
    agent = QuestionReviewer()
    result = await agent.review_question("Is it a mammal?", 0)
    assert result.good_question


if __name__ == "__main__":
    pytest.main()
