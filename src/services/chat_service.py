from src.services.graph import get_graph

async def ask_question(question: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    graph = await get_graph()
    
    async for message, metadata in graph.astream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="messages",
        config=config,
    ):
        node = metadata.get("langgraph_node")
        if node in ("should_query", "tools"):
            continue
        yield message.content