from langchain_cohere import ChatCohere
from langchain_openai import OpenAI
from langchain_cohere import CohereEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langgraph.graph import START, END, StateGraph, MessagesState
from langchain import hub
from langchain_core.documents import Document
from langchain_core.tools import tool
from typing_extensions import List, TypedDict
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver


from src.services.vector_store import VectorStore
from src.config.config import LLMProvider, app_config

# Shared Resources
vector_store = VectorStore()
prompt = hub.pull("rlm/rag-prompt")

# LLM Initialization
def get_llm():
    if app_config.model.llm_provider == LLMProvider.OPENAI:
        return OpenAI(
            api_key=app_config.model.api_key,
            model=app_config.model.llm_model
        )
    return ChatCohere(
        cohere_api_key=app_config.model.api_key,
        model=app_config.model.llm_model
    )

llm = get_llm()

# Embedding Model Initialization
def get_embedding_model():
    if app_config.model.llm_provider == LLMProvider.OPENAI:
        return OpenAIEmbeddings(
            api_key=app_config.model.api_key,
            model=app_config.model.embedding_model
        )
    return CohereEmbeddings(
        cohere_api_key=app_config.model.api_key,
        model=app_config.model.embedding_model
    )

embedding_model = get_embedding_model()

# Retrieve Tool
@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """
    Perform a similarity search to retrieve relevant information.
    """
    embedding = embedding_model.embed_query(query)
    rows = vector_store.similarity_search(embedding, limit=10)
    context = [
        Document(
            page_content=row["text"],
            metadata={
                "source_key": row["source_key"],
                "source_label": row["source_label"]
            }
        ) for row in rows
    ]
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in context
    )
    return serialized, context

# Query or Respond
def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

tools = ToolNode([retrieve])

# Generate Response
def generate(state: MessagesState):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    response = llm.invoke(prompt)
    return {"messages": [response]}

# Ask Question Function
memory = MemorySaver()
config = {"configurable": {"thread_id": "abc123"}}
def ask_question(question: str):
    # Specify an ID for the thread

    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node(query_or_respond)
    graph_builder.add_node(tools)
    graph_builder.add_node(generate)

    graph_builder.set_entry_point("query_or_respond")
    graph_builder.add_conditional_edges(
        "query_or_respond",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)

    graph = graph_builder.compile(checkpointer=memory)
    messages = []
    for message, metadata in graph.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="messages",
        config=config,
    ):
        print("###")
        yield message.content
        print(message.content, end="|")
        # messages.append(step["messages"][-1].content)
        # step["messages"][-1].pretty_print()

    print("###########")
    print(messages)
    # return "Hi"
