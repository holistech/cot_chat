from pprint import pprint
import pyperclip
import datetime
import streamlit as st
import yaml
from litellm import completion
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from litellm import completion, ModelResponse
import logging

load_dotenv()


# Pydantic models
class LLMAgentModel(BaseModel):
    id: str = Field(..., description="The unique identifier of the agent")
    llm: str = Field(..., description="The LLM that should be used for inference. It will be a parameter for the "
                                      "litellm library to pick the correct model",
                     examples=["gpt-4o", "gpt-4o-mini", "gemini/gemini-pro", "claude-3-5-sonnet-20240620",
                               "mistral/open-mixtral-8x7b", "groq/llama3-8b-8192", "groq/mixtral-8x7b-32768",
                               "together_ai/togethercomputer/llama-2-70b, together_ai/Qwen/Qwen2-72B-Instruct, "
                               "together_ai/meta-llama/Llama-3-70b-chat-hf"])
    system_prompt: str = Field(..., description="The system prompt for the specific agent")
    user_prompt: str = Field(..., description="The user prompt of the specific agent that must include {user_question}"
                                              " and {previous_answer} format strings for later text inclusion")
    order: int = Field(default=1, description="The order of the argent.")
    name: str = Field(default="LLM Node", description="The name of the agent that is displayed in the diagram.")
    max_tokens: int = Field(default=4096, description="The maximum number of tokens to write the answer")
    temperature: float = Field(default=0.1, description="The temperature for the LLM")
    max_cot_iterations: int = Field(default=10,
                                    description="The maximum number of iterations in a chain of thought thinking stream")

    def __str__(self):
        return f"LLMAgent(id={self.id}, llm={self.llm}, type={self.order}, type={self.name})"


class LLMAgentGraphModel(BaseModel):
    agents: List[LLMAgentModel] = []


# Function to load agents from YAML
def load_agents_from_yaml(file_path):
    with open(file_path, 'r') as file:
        agents_data = yaml.safe_load(file)

    agents = [LLMAgentModel(**agent_data) for agent_data in agents_data]
    return LLMAgentGraphModel(agents=agents)


# LLM call function using litellm


def llm_call(agent: LLMAgentModel, messages: List[Dict[str, str]], max_history: int):
    system_message = {"role": "system", "content": agent.system_prompt}
    history_messages = messages[-max_history:]
    llm_messages = [system_message] + history_messages

    pprint(llm_messages)

    try:
        response = completion(
            model=agent.llm,
            messages=llm_messages,
            stream=True,
            max_tokens=agent.max_tokens,
            temperature=agent.temperature
        )
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk
    except Exception as e:
        logging.error(f"Error in LLM call: {str(e)}")
        yield ModelResponse(choices=[{"delta": {"content": f"Error: {str(e)}"}}])


# Chain of Thought function
def chain_of_thought(agent_graph: LLMAgentGraphModel, user_question: str, chat_history: List[Dict[str, str]],
                     max_history: int, max_iterations: int):
    first_agent, second_agent, third_agent, fourth_agent = agent_graph.agents

    # First agent (unchanged)
    first_response = ""
    yield f"### First Agent ({first_agent.name}):\n\n"
    for chunk in llm_call(first_agent, chat_history, max_history):
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            content = content.replace(">", ">\n")
            first_response += content
            yield content

    # Second and Third agents (loop)
    loop_response = first_response

    yield f"\n\n### Entering reasoning loop:\n\n"
    for i in range(max_iterations):
        # Second agent
        second_input = second_agent.user_prompt.format(user_request=user_question, previous_answer=loop_response)
        second_agent_messages = chat_history + [
            {"role": "assistant", "content": first_response},
            {"role": "user", "content": second_input}
        ]
        yield f"\n\n### Iteration {i + 1}\n"
        yield f"\n\n#### Agent {second_agent.name}:\n\n"
        for chunk in llm_call(second_agent, second_agent_messages, max_history):
            content = chunk.choices[0].delta.content
            content = content.replace(">", ">\n")
            loop_response += content
            yield content

        # Third agent (new)
        third_input = third_agent.user_prompt.format(user_request=user_question,
                                                     previous_answer=loop_response)
        third_agent_messages = chat_history + [
            {"role": "assistant", "content": first_response},
            {"role": "user", "content": third_input}
        ]
        yield f"\n\n#### Agent {third_agent.name}:\n\n"
        for chunk in llm_call(third_agent, third_agent_messages, max_history):
            content = chunk.choices[0].delta.content
            content = content.replace(">", ">\n")
            loop_response += content
            yield content


        if "<final>Complete</final>".lower() in loop_response.lower().replace(" ", "").replace("\n", ""):
            break

    # Fourth agent (previously third)
    fourth_response = ""
    fourth_input = fourth_agent.user_prompt.format(user_request=user_question, previous_answer=loop_response)
    fourth_agent_messages = chat_history + [
        {"role": "assistant", "content": fourth_input},
        {"role": "user", "content": loop_response},
    ]

    yield f"\n\n### Fourth Agent ({fourth_agent.name}):\n\n"
    for chunk in llm_call(fourth_agent, fourth_agent_messages, max_history):
        content = chunk.choices[0].delta.content
        content = content.replace(">", ">\n")
        fourth_response += content
        yield content


def run_streamlit_app():
    st.title("Agent Chat")

    # YAML file uploader
    uploaded_file = st.sidebar.file_uploader("Load new agent definitions", type="yaml")
    if uploaded_file is not None:
        st.session_state.agent_graph = load_agents_from_yaml(uploaded_file)
        st.sidebar.success("New agent definitions loaded successfully!")

    # Sidebar
    st.sidebar.title("Agents")
    for agent in st.session_state.agent_graph.agents:
        st.sidebar.write(f"- {agent.name}")
    first_agent, second_agent, third_agent, fourth_agent = st.session_state.agent_graph.agents

    # Max history setting
    max_history = st.sidebar.slider("Max Chat History Entries", min_value=1, max_value=40, value=10)

    # New: Max iterations setting
    max_iterations = st.sidebar.slider("Max Iterations", min_value=1, max_value=20, value=5)

    # Copy conversation to clipboard
    if st.sidebar.button("Copy Conversation to Clipboard"):
        conversation = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
        pyperclip.copy(conversation)
        st.sidebar.success("Conversation copied to clipboard!")

    # Save conversation to file
    default_filename = f"conversation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    if st.sidebar.button("Save Conversation to File"):
        conversation = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
        with open(default_filename, "w", encoding="utf-8") as f:
            f.write(conversation)
        st.sidebar.success(f"Conversation saved to {default_filename}")
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("What is your question?"):
        prompt = first_agent.user_prompt.format(user_request=prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Chain of Thought process
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            for response in chain_of_thought(st.session_state.agent_graph, prompt, st.session_state.messages,
                                             max_history, max_iterations):
                full_response += response
                response_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})


# Main execution
if __name__ == "__main__":
    st.set_page_config(page_title="Chain of Thought Chat", page_icon="🤖", layout="wide")

    # Load initial agents
    if 'agent_graph' not in st.session_state:
        st.session_state.agent_graph = load_agents_from_yaml('chain_of_thought_agents.yaml')

    run_streamlit_app()
