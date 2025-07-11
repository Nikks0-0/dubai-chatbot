import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tools import search_flights, make_itinerary

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.3
)

def flight_search_agent(origin, destination, start_date, end_date, budget):
    flights = search_flights(origin, destination, start_date, end_date, budget)
    if not flights or "error" in flights[0]:
        return flights[0].get("error", "No flights found.")
    reply = "Here are the best flight deals I found:\n"
    for f in flights:
        reply += (
            f"- {f['airline']} {f['flight_no']}: {f['departure']} → {f['arrival']} "
            f"for {f['price']} {f['currency']}\n"
        )
    return reply

def itinerary_agent(start_date, end_date, budget):
    prompt = (
        f"You are a Dubai travel planner. Create a detailed daily itinerary for a trip to Dubai "
        f"from {start_date} to {end_date} with a total budget of {budget} USD. "
        f"Include must-see attractions, dining, and local experiences. Format as a day-by-day plan."
    )
    response = llm.invoke(prompt)
    return response.content

def followup_agent(user_message, state):
    # Use GPT-4o Mini to answer any follow-up user queries about Dubai travel
    context = (
        f"User has planned a Dubai trip from {state.get('start_date')} to {state.get('end_date')} "
        f"with a budget of {state.get('budget')} USD. "
        f"Previous itinerary and flight details have been shared. "
        f"Now, answer the user's follow-up question in a helpful, friendly, and concise way. "
        f"User's message: {user_message}"
    )
    response = llm.invoke(context)
    return response.content

def supervisor_agent(user_input, state):
    # Initial step or missing state
    if not state or state.get("step") == "ask_dates":
        if user_input.get("start_date") and user_input.get("end_date"):
            state["start_date"] = user_input.get("start_date")
            state["end_date"] = user_input.get("end_date")
            state["step"] = "ask_budget"
            return "Great! What's your total budget for this Dubai trip (in USD)?", state
        else:
            state["step"] = "ask_dates"
            return "Please tell me your trip start and end dates (YYYY-MM-DD).", state

    # After dates, ask for budget
    if state.get("step") == "ask_budget":
        if user_input.get("budget"):
            state["budget"] = user_input.get("budget")
            state["step"] = "done"
            origin = "DEL"  # You can make this dynamic if needed
            destination = "DXB"
            flights = flight_search_agent(origin, destination, state["start_date"], state["end_date"], state["budget"])
            itinerary = itinerary_agent(state["start_date"], state["end_date"], state["budget"])
            reply = (
                f"✈️ **Best Flight Deals:**\n{flights}\n\n"
                f"🗺️ **Your Dubai Itinerary:**\n{itinerary}\n\n"
                f"Do you have any other questions or want more details about your trip? "
                f"Ask me anything about Dubai travel!"
            )
            return reply, state
        else:
            return "Please enter your total budget for this Dubai trip (in USD).", state

    # After itinerary, answer any further user queries
    if state.get("step") == "done":
        if user_input.get("message"):
            reply = followup_agent(user_input["message"], state)
            return reply, state
        else:
            origin = "DEL"
            destination = "DXB"
            flights = flight_search_agent(origin, destination, state["start_date"], state["end_date"], state["budget"])
            itinerary = itinerary_agent(state["start_date"], state["end_date"], state["budget"])
            reply = (
                f"✈️ **Best Flight Deals:**\n{flights}\n\n"
                f"🗺️ **Your Dubai Itinerary:**\n{itinerary}\n\n"
                f"Do you have any other questions or want more details about your trip? "
                f"Ask me anything about Dubai travel!"
            )
            return reply, state

    # Default fallback
    state["step"] = "ask_dates"
    return "Welcome! For your Dubai trip, please enter your start and end dates (YYYY-MM-DD).", state
