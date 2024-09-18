# cot_chat

Please create a streamlit litellm chat application that implements a three agent Chain Of Thought chat application.

Use litellm to create the llm calls.
Use streamlit as chat interface
Use the provided pydantic LLMAgentGraphModel and LLMAgentModel to specify the LLM agents.

Three agents of type LLMAgentModel must be used to implement the chain of thought approach.

The first agent get the question from the user and creates the first iteration of the thought.
The user question must be put into the Agent user prompt identified as {user_question}.

The second agent must be run in a loop. Hence, it will get the user question and the output of the first agent as input.
The output of the second agent will be append to the output of the first agent and will be input of the second agent again,
until the break criteria is reached or the number of iterations was reached. The break criteria is when the second agent puts the
string <final>Confirmed</final> into the output.

The last agent gets the full output (first agent and all appended outputs of the second agent) as input to consolidate
the conclusion.

The output of all agents must be streamed into the streamlit chat window, so that the user can follow the chain of thought
in realtime.

The GUI:
Create a streamlit chat interface that provides a user input window and a chat window that shows the history of
the chat shows the output of the agents in realtime. Implement a side bar in which the agent names are present and an interface to load a new
YAML BASED AGENT DEFINITION as new agents.

Hence, agent definition from YAML must be loaded and used for LLM inference.

Please analyse the requirements above and implement them step by step.