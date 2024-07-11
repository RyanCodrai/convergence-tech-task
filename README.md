# convergence-tech-task
LLM Agents take-home task for convergence AI


# Planning

graph TD
    A[Topic Creator] -->|Creates topic| B[Game Start]
    B --> C[Question Asker]
    C -->|Proposes question| D[Question Planner]
    D -->|Refines question| C
    C -->|Finalizes question| E[Question Answerer]
    E -->|Provides yes/no answer| F{Correct Guess?}
    F -->|No| C
    F -->|Yes| G[Game End]
    C -->|20 questions asked| G
