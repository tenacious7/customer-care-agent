import os
import json

from openai import OpenAI

from graph.state import CustomerState

from tools.orders import get_order
from tools.orders import get_product

llm = OpenAI(
    base_url="http://localhost:3001/v1",
    api_key=os.getenv("FREELLM_API_KEY", "dummy"),
)


def classify_intent(state: CustomerState):

    response = llm.chat.completions.create(
        model="auto",
        messages=[
            {
                "role": "system",
                "content": """
You are a customer support intent classifier.

Classify the customer's message into exactly ONE of these intents:

ORDER_STATUS
REFUND
PRODUCT_INFO
HUMAN_SUPPORT
GENERAL

Also extract the order number if one is mentioned.

Return ONLY valid JSON in this exact format:

{
    "intent": "ORDER_STATUS",
    "order_number": "ORD1001"
}

If there is no order number, return:

{
    "intent": "GENERAL",
    "order_number": ""
}

Rules:

- ORDER_STATUS → customer asks about the status, location, delivery, or arrival of an order.
- REFUND → customer wants to return, cancel, or get a refund for an order.
- PRODUCT_INFO → customer asks about a product.
-If the customer asks about "it", "this", "that","what about", "would it", "is it", "how about",etc. and an active product exists,classify it as PRODUCT_INFO.
- HUMAN_SUPPORT → customer wants to talk to a human/support agent.
- GENERAL → general questions that do not belong to the above categories.
- If an order number is present, extract it exactly.
- If no order number is present, use an empty string.

Do not provide explanations.
Do not provide additional text.
""",
            },
            {
                "role": "user",
                "content": state["message"],
            },
        ],
        response_format={
            "type": "json_object"
        },
    )

    content = response.choices[0].message.content

    data = json.loads(content)

    return {
        "intent": data["intent"],
        "order_number": data.get("order_number", ""),
    }

#order status node
import re

from tools.orders import get_order


def order_status(state: CustomerState):

    match = re.search(r"\bORD\d+\b", state["message"], re.IGNORECASE)

    if not match:
        return {
            "response": "Please provide your order number, for example ORD1001."
        }

    order_number = match.group(0).upper()

    order = get_order(order_number)

    if not order:
        return {
            "response": f"I couldn't find an order with the number {order_number}."
        }

    return {
        "order_number": order_number,
        "response": (
            f"Your order {order['order_number']} for {order['product']} "
            f"is currently {order['status']}. "
            f"Estimated delivery: {order['estimated_delivery']}."
        )
    }





def refund(state: CustomerState):

    order_number = state.get("order_number")

    if not order_number:
        return {
            "response": "Please provide your order number so I can check the refund."
        }

    order = get_order(order_number)

    if not order:
        return {
            "response": f"I couldn't find order {order_number}."
        }

    status = order["status"]

    if status in ["SHIPPED", "PROCESSING"]:
        return {
            "response": (
                f"Your order {order_number} is currently {status}.\n\n"
                f"Product: {order['product']}\n\n"
                "This order is eligible for a refund."
            )
        }

    return {
        "response": (
            f"Your order {order_number} is currently {status}.\n\n"
            "This order is not eligible for a refund."
        )
    }





def product_info(state: CustomerState):

    # If we already know which product the customer is talking about,
    # use the product from short-term memory.
    if state.get("product_name"):

        product = get_product(state["product_name"])

        if not product:
            return {
                "response": "I couldn't find that product anymore."
            }

    else:
        # No product in memory → ask the LLM to identify it
        response = llm.chat.completions.create(
            model="auto",
            messages=[
                {
                    "role": "system",
                    "content": """
You are a customer support assistant.

Identify the product name mentioned by the customer.

Return ONLY valid JSON:

{
    "product_name": "..."
}

If no product is mentioned, return:

{
    "product_name": ""
}

Do not provide explanations.
"""
                },
                {
                    "role": "user",
                    "content": state["message"]
                }
            ],
            response_format={
                "type": "json_object"
            }
        )

        data = json.loads(
            response.choices[0].message.content
        )

        product_name = data["product_name"]

        if not product_name:
            return {
                "response": "Which product would you like information about?"
            }

        product = get_product(product_name)

        if not product:
            return {
                "response": f"I couldn't find a product matching '{product_name}'."
            }

    # Generate the actual customer response using the LLM
    response = llm.chat.completions.create(
        model="auto",
        messages=[
            {
                "role": "system",
                "content": f"""
You are a helpful customer support agent.

Answer the customer's question using ONLY the product information below.

Product:
{product["name"]}

Description:
{product["description"]}

Price:
₹{product["price"]}

Stock:
{product["stock"]}

Do not invent product specifications that are not provided.
If the customer asks for an opinion or recommendation, answer naturally
based on the available product information.
"""
            },
            {
                "role": "user",
                "content": state["message"]
            }
        ]
    )

    return {
        "product_name": product["name"],
        "active_product": product,
        "response": response.choices[0].message.content
    }

def human_support(state: CustomerState):

    return {
        "response": (
            "Sure, I can connect you with a human support agent. "
            "Please wait while we transfer your request."
        )
    }


def general(state: CustomerState):

    response = llm.chat.completions.create(
        model="auto",
        messages=[
            {
                "role": "system",
                "content": """
You are a helpful customer support assistant.

Answer general customer questions naturally and briefly.

You can help with:
- General greetings
- Basic help navigating the support system
- Questions about how to contact support
- General questions about shopping and orders

Do not invent company policies, prices, delivery times,
refund rules, warranties, or product specifications.

If the customer asks for specific information that you do not have,
tell them that you need more information or that a support agent can help.

Keep responses concise and friendly.
"""
            },
            {
                "role": "user",
                "content": state["message"]
            }
        ]
    )

    return {
        "response": response.choices[0].message.content
    }





def product_conversation(state: CustomerState):

    print("🔥 PRODUCT_CONVERSATION NODE REACHED")
    product_name = state.get("product_name")

    if not product_name:
        return {
            "response": "How can I help you?"
        }

    product = get_product(product_name)

    if not product:
        return {
            "response": "I couldn't find the product information."
        }

    response = llm.chat.completions.create(
        model="auto",
        messages=[
            {
                "role": "system",
                "content": f"""
You are a helpful customer support agent.

The customer is currently discussing this product:

Product: {product["name"]}
Description: {product["description"]}
Price: ₹{product["price"]}
Stock: {product["stock"]}

Answer the customer's current question naturally.

Use the product information above when relevant.
Do not invent product specifications.
"""
            },
            {
                "role": "user",
                "content": state["message"]
            }
        ]
    )

    return {
        "response": response.choices[0].message.content,
        "product_name": product["name"]
    }