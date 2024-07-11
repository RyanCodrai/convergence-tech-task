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

In this solution we have 4 agents, a topic creator, a question asker, a quesiton planner, and a question answerer. The question answerer's job is comparatively easy compared with the question asker and due to the limited number of questions a question planner is used to ensure maximum utility of the questions asked. We observe that the game of 20 questions follows a simple and straightforward turn-taking flow which doesn't require clever decision making from our agents. Therefore, to ensure reliable interactions between our agents we allow them to interact with each other programatically. Each turn, the question asker confers with the question planner n times before finally asking their question. Metadata captures whether this question is a successful guess that ends the game early.

We use langchain to create an Agent baseclass from which all of our agents will inherit. Each agent will have memory of their conversations with other agents and will also be able to provide structured output if required such as in the case where we check if the topic has been guessed correctly.

To create a reproducable development environment we container the application. We add monitoring through the use of LangFuse and logging statements and then we optimise the application by ensuring the LLM calls are completed asyncronously.
