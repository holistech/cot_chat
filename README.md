# Chain of Thought Chat

This is a demonstration of a Chain of Thought (CoT) chat application that employs three agents to apply the CoT paradigm within a Streamlit interface. It is based on the Mixture of Specialized Agent Graphs (MosAG) approach from Holistech, which is designed to implement advanced agent graphs for deep knowledge retrieval and research.

## Web Interface

The Streamlit web interface offers a simple chat window for asking questions, viewing the thought process of the various agents, and saving the entire conversation as a text file.

![image](https://github.com/user-attachments/assets/bd3a682d-6bd9-4263-93d4-dbcfc2e461fc)

## Agents
The application utilizes three agents to implement the CoT methodology:

1. **Initial Chain of Thought reasoning agent**: This agent analyzes the user’s question and suggests an initial solution.
2. **Iterative CoT agent**: This agent iteratively refines the first agent's solution until either a satisfactory conclusion is reached or the maximum number of iterations has been performed.
3. **CoT aggregator and explainer**: This agent consolidates the entire conversation and presents the results in a digestible format.

These agents are specified in a YAML configuration file, which includes the necessary language models, system prompts, and user prompts and the maximum number of CoT iterations. This allows for the assignment of a unique LLM to each agent individually within the YAML configuration. Any LLM definition supported by LiteLLM can be used, such as:

- claude-3-5-sonnet-20240620
- gpt-4o-mini
- gpt-4o

## Installation

1. Create a virtual Python environment and install all required dependencies using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

2. Create a `.env` file and store your API keys, allowing you to use different language models for testing the CoT approach.
3. Run the Streamlit application, open your browser, and start exploring the CoT approach:

    ```bash
    streamlit run chat.py
    ```

# Example application postgresql based job schedular

Please provide a solution for the following requirements:

I need a comprehensive Python solution to implement a job scheduler using the postgresql pub/sub system. 
The job scheduler must run, stop, remove and cancel docker container that uses images from a docker image repository. 
Only postgresql, Python and docker should be used for the implementation. Do not use Redis or celery!
A REST interface must be designed, so that job can be startet, cancelled/stopped, paused and resumed. 
It is important that the REST API must be asynchronous. 
Hence additional endpoints are required to get the current log of the docker container so that a client can track the progress of a computation within a docker container.
Use FastAPI for the REST interface.

Tools to use:
- Python
- postgresql
- docker
- FastAPI

Use different file for postgresql approach, REST interface