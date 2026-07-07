"""
AI Feature #2: AI Chatbot for Customer Support
--------------------------------------------------
An intent-classification chatbot: user text is normalised, matched against
weighted keyword sets for each supported intent, and the highest-scoring
intent's response template is returned. This "rule + keyword scoring"
approach is a common lightweight NLU technique used by real support bots
before/instead of a full LLM, and is fast + fully explainable + free to run.
"""
import re

INTENTS = {
    'greeting': {
        'keywords': ['hi', 'hello', 'hey', 'good morning', 'good evening', 'namaste'],
        'responses': [
            "Hello! 👋 Welcome to StayEase. I can help with room availability, "
            "check-in/out times, bookings, hotel facilities or cancellations. What do you need?"
        ],
    },
    'availability': {
        'keywords': ['available', 'availability', 'vacancy', 'free room', 'any room', 'book a room'],
        'responses': [
            "You can check live room availability on our Rooms page — use the search "
            "and filter tools to pick your dates, budget and guest count. Want me to "
            "take you there?"
        ],
    },
    'checkin_checkout': {
        'keywords': ['check-in', 'check in', 'checkin', 'check-out', 'check out', 'checkout', 'timing', 'time'],
        'responses': [
            "Standard check-in is from 12:00 PM and check-out is by 11:00 AM. "
            "Early check-in / late check-out can be requested at booking, subject to availability."
        ],
    },
    'booking_process': {
        'keywords': ['how to book', 'booking process', 'reserve', 'reservation', 'how do i book'],
        'responses': [
            "Booking is simple: 1) Search rooms by date & guests, 2) Pick a room and "
            "review details, 3) Enter guest info, 4) Pay securely via UPI or Card, "
            "5) Get an instant confirmation + downloadable PDF invoice."
        ],
    },
    'facilities': {
        'keywords': ['facility', 'facilities', 'amenities', 'wifi', 'pool', 'gym', 'breakfast', 'parking'],
        'responses': [
            "Most rooms include free Wi-Fi, AC, breakfast and 24x7 room service. "
            "Premium rooms add a pool, gym access and free parking — check each "
            "room's amenities list for specifics."
        ],
    },
    'cancellation': {
        'keywords': ['cancel', 'cancellation', 'refund', 'reschedule'],
        'responses': [
            "You can cancel from 'My Bookings' in your dashboard up to 24 hours "
            "before check-in for a full refund. Cancellations after that are "
            "subject to a one-night charge."
        ],
    },
    'payment': {
        'keywords': ['payment', 'pay', 'upi', 'card', 'price', 'cost', 'invoice'],
        'responses': [
            "We accept UPI and Credit/Debit cards. Once payment succeeds you'll "
            "get an instant confirmation and can download a PDF invoice from your dashboard."
        ],
    },
    'thanks': {
        'keywords': ['thank', 'thanks', 'thank you', 'great', 'awesome'],
        'responses': ["You're welcome! Is there anything else I can help you with? 😊"],
    },
    'goodbye': {
        'keywords': ['bye', 'goodbye', 'see you'],
        'responses': ["Goodbye! Have a wonderful stay with StayEase. 🏨"],
    },
}

FALLBACK_RESPONSE = (
    "I'm not fully sure about that yet — I can help with room availability, "
    "check-in/out timings, the booking process, hotel facilities, payments, or "
    "cancellations. Could you rephrase your question?"
)


def _normalize(text: str) -> str:
    return re.sub(r'[^a-z0-9\s]', '', text.lower()).strip()


def get_bot_response(message: str):
    """Classify the user's message into an intent and return a reply."""
    text = _normalize(message)
    best_intent, best_score = None, 0

    for intent, data in INTENTS.items():
        score = sum(1 for kw in data['keywords'] if kw in text)
        if score > best_score:
            best_score = score
            best_intent = intent

    if best_intent:
        response = INTENTS[best_intent]['responses'][0]
        return response, best_intent

    return FALLBACK_RESPONSE, 'unknown'
