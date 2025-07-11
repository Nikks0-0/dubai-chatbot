import requests
import os
from dotenv import load_dotenv

load_dotenv()

def search_flights(origin, destination, start_date, end_date, budget):
    AMADEUS_API_KEY = os.getenv('AMADEUS_API_KEY')
    AMADEUS_API_SECRET = os.getenv('AMADEUS_API_SECRET')

    token_url = 'https://test.api.amadeus.com/v1/security/oauth2/token'
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': AMADEUS_API_KEY,
        'client_secret': AMADEUS_API_SECRET
    }
    token_response = requests.post(token_url, data=token_data)
    if token_response.status_code != 200:
        return [{"error": "Failed to authenticate with Amadeus API."}]
    access_token = token_response.json().get('access_token')

    search_url = 'https://test.api.amadeus.com/v2/shopping/flight-offers'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        'originLocationCode': origin,
        'destinationLocationCode': destination,
        'departureDate': start_date,
        'adults': 1,
        'max': 5,
        'currencyCode': 'USD'
    }
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        return [{"error": "Failed to fetch flight offers from Amadeus API."}]
    data = response.json()

    results = []
    for offer in data.get('data', []):
        itineraries = offer.get('itineraries', [])
        price = offer.get('price', {}).get('total')
        currency = offer.get('price', {}).get('currency')
        for itinerary in itineraries:
            segments = itinerary.get('segments', [])
            if segments:
                seg = segments[0]
                airline = seg.get('carrierCode')
                flight_no = seg.get('number')
                dep = seg.get('departure', {})
                arr = seg.get('arrival', {})
                results.append({
                    "airline": airline,
                    "flight_no": flight_no,
                    "departure": f"{dep.get('iataCode', '')} {dep.get('at', '')}",
                    "arrival": f"{arr.get('iataCode', '')} {arr.get('at', '')}",
                    "price": price,
                    "currency": currency
                })
    if not results:
        return [{"error": "No flights found for the given dates and budget."}]
    if budget:
        results = [f for f in results if float(f['price']) <= float(budget)]
        if not results:
            return [{"error": "No flights found within your budget."}]
    return results

def make_itinerary(start_date, end_date, budget):
    # Placeholder: Use GPT-4o Mini for dynamic itinerary in agents.py
    return [
        {"day": "Day 1", "plan": "Arrive in Dubai, check-in to hotel, evening at Dubai Mall and Fountain Show."},
        {"day": "Day 2", "plan": "Visit Burj Khalifa, lunch at Souk Al Bahar, evening at Jumeirah Beach."},
        {"day": "Day 3", "plan": "Desert Safari with dinner, morning at Museum of the Future."},
        {"day": "Day 4", "plan": "Shopping at Mall of the Emirates, Ski Dubai, departure."}
    ]
