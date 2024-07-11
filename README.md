# convergence-tech-task
LLM Agents take-home task for convergence AI


# Running the demo
1. **Compile dependencies** by running `make deps` in the root project directory .
2. **Build Docker image** by running `make build` in the root project directory .
3. **Start containers and enter bash session**  by running `make start` in the root project directory.
4. **Run the game (inside container)** by running `python3 game.py` in the docker container.

# Planning

### Agent architechture
![Agent Architechture Diagram](readme_resources/agent_architechture.png)

### Design approach

In this solution we have 4 agents, a topic creator, a question asker, a quesiton planner, and a question answerer. The question answerer's job is comparatively easy compared with the question asker and we therefore do not break it down into smaller agents. Whereas a question planner acompanies the question asker to ensure maximum utility of the questions asked. We observe that the game of 20 questions follows a simple and straightforward turn-taking flow which doesn't require clever decision making from our agents. Therefore, to ensure reliable interactions between our agents we allow them to interact with each other programatically rather than allowing them to choose their own interactions. Each turn, the question asker confers with the question planner n times before finally asking a question. Metadata captures whether this question is a successful guess that ends the game early.

We use langchain to create an Agent baseclass from which all of our agents will inherit. Each agent has a memory of their conversations with other agents and will also can structure their output into a pydantic model so that we can reason about their outputs if required.

To create a reproducable development environment we container the application. We add monitoring through the use of LangFuse and logging statements and then we optimise the application by ensuring the LLM calls are completed asyncronously.


### Evaluation
Although we don't directly evaluate the appraoch taken here we have the data in Langfuse to be able to assess the quality of the LLM responses to inform the improvements we'll make for the next iterations.

The next step for this project would be to allow per-run setting of prompts. This could be appraoched in a number of ways 
