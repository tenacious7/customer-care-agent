from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from graph.state import CustomerState
from graph.nodes import (
    classify_intent,
    order_status,
    refund,
    product_info,
    product_conversation,
    human_support,
    general,
)


def route_intent(state: CustomerState):

    if (
        state["intent"] == "PRODUCT_INFO"
        and state.get("active_product")
    ):
        return "PRODUCT_CONVERSATION"

    return state["intent"]


graph_builder = StateGraph(CustomerState)

# Nodes
graph_builder.add_node("classify_intent", classify_intent)
graph_builder.add_node("order_status", order_status)
graph_builder.add_node("refund", refund)
graph_builder.add_node("product_info", product_info)
graph_builder.add_node("product_conversation",product_conversation)
graph_builder.add_node("human_support", human_support)
graph_builder.add_node("general", general)

# START → classifier
graph_builder.add_edge(START, "classify_intent")

# Classifier → correct node
graph_builder.add_conditional_edges(
    "classify_intent",
    route_intent,
    {
        "ORDER_STATUS": "order_status",
        "REFUND": "refund",
        "PRODUCT_INFO": "product_info",
        "PRODUCT_CONVERSATION": "product_conversation",
        "HUMAN_SUPPORT": "human_support",
        "GENERAL": "general",
    },
)

# Nodes → END
graph_builder.add_edge("order_status", END)
graph_builder.add_edge("refund", END)
graph_builder.add_edge("product_info", END)
graph_builder.add_edge("human_support", END)
graph_builder.add_edge("general", END)
graph_builder.add_edge("product_conversation", END)


# Short-term memory
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()

customer_graph = graph_builder.compile(
    checkpointer=memory
)