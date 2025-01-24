import json
from langchain_cohere import ChatCohere
from langchain_openai import OpenAI
from langchain_cohere import CohereEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langgraph.graph import END, StateGraph, MessagesState
from langchain import hub
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from src.database import get_db_connection

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
    serialized = "SERIALIZED_SOURCES: " + json.dumps(
        [
            {"metadata": doc.metadata, "content": doc.page_content}
            for doc in context
        ],
        indent=2
    )
    return serialized, context

# Query function
def should_query(state: MessagesState):
    """Determine if we need to query for information."""
    # Create a chain that can use tools
    chain = llm.bind_tools([retrieve])
    
    # Run the chain and get the response
    messages = state["messages"]
    response = chain.invoke(messages)
    
    # Check if we need tools by looking for tool calls
    if hasattr(response, "tool_calls") and response.tool_calls:
        # If we need tools, return the response with tool calls
        return {"messages": messages + [response]}
    else:
        # If we don't need tools, return just the original messages
        # This will make the should_use_tools function return END
        return {"messages": messages}

tools = ToolNode([retrieve])

# Response function
def direct_response(state: MessagesState):
    """Generate direct response without tools."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

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
    system_message_content = app_config.model.system_prompt.format(docs_content=docs_content)
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

def should_use_tools(state: MessagesState) -> str:
    """Determine if we should use tools based on the last message."""
    last_message = state["messages"][-1]
    # Check if the message has tool calls
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

async def ask_question(question: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}

    graph_builder = StateGraph(MessagesState)
    
    # Add nodes
    graph_builder.add_node("should_query", should_query)
    graph_builder.add_node("direct_response", direct_response)
    graph_builder.add_node(tools)
    graph_builder.add_node(generate)

    # Set entry point
    graph_builder.set_entry_point("should_query")
    
    # Add edges with custom condition
    graph_builder.add_conditional_edges(
        "should_query",
        should_use_tools,
        {
            "tools": "tools",  # If tools are needed, go to tools
            END: "direct_response",  # If no tools needed, go to direct response
        },
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)
    graph_builder.add_edge("direct_response", END)

    async with get_db_connection() as pool:
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()
        graph = graph_builder.compile(checkpointer=checkpointer)
        async for message, metadata in graph.astream(
            {"messages": [{"role": "user", "content": question}]},
            stream_mode="messages",
            config=config,
        ):
            node = metadata.get("langgraph_node")
            # Skip messages from tools node
            if node == "tools":
                continue
            # Skip messages from should_query node
            if node == "should_query":
                continue
            # Yield messages from direct_response and generate nodes
            print(message.content)
            yield message.content
