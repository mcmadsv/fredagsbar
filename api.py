
from flask import Flask, request

app = Flask(__name__)

events = [
    {"id": 1, "title": "Quizaften", "date": "2026-11-13", "capacity": 3, "participants": ["Anna", "Bo"]},
    {"id": 2, "title": "Brætspilsaften", "date": "2026-11-20", "capacity": 5, "participants": ["Emil"]},
    {"id": 3, "title": "Beerpong-turnering", "date": "2026-11-27", "capacity": 2, "participants": []},
]


def find_event(event_id):
    for event in events:
        if event["id"] == event_id:
            return event
    return None


@app.get("/events")
def get_events():
    return events


@app.get("/events/<int:event_id>")
def get_event(event_id):
    event = find_event(event_id)
    if event is None:
        return {"error": "Eventet findes ikke"}, 404
    return event


@app.post("/events")
def create_event():
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not all(key in data for key in ("title", "date", "capacity")):
        return {"error": "title, date og capacity er påkrævet"}, 400

    if (not isinstance(data["title"], str) or not data["title"].strip()
            or not isinstance(data["date"], str) or not data["date"].strip()):
        return {"error": "title og date skal være udfyldte tekster"}, 400

    if type(data["capacity"]) is not int or data["capacity"] <= 0:
        return {"error": "capacity skal være et positivt heltal"}, 400

    new_event = {
        "id": max((event["id"] for event in events), default=0) + 1,
        "title": data["title"],
        "date": data["date"],
        "capacity": data["capacity"],
        "participants": [],
    }

    events.append(new_event)
    return new_event, 201


@app.post("/events/<int:event_id>/signups")
def signup(event_id):
    event = find_event(event_id)

    if event is None:
        return {"error": "Eventet findes ikke"}, 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not isinstance(data.get("name"), str) or not data["name"].strip():
        return {"error": "name er påkrævet"}, 400

    name = data["name"].strip()

    if name in event["participants"]:
        return {"error": "Personen er allerede tilmeldt"}, 409

    if len(event["participants"]) >= event["capacity"]:
        return {"error": "Eventet er fuldt"}, 409

    event["participants"].append(name)
    return event, 201


@app.delete("/events/<int:event_id>/signups/<name>")
def cancel_signup(event_id, name):
    event = find_event(event_id)

    if event is None:
        return {"error": "Eventet findes ikke"}, 404

    if name not in event["participants"]:
        return {"error": "Tilmeldingen findes ikke"}, 404

    event["participants"].remove(name)
    return "", 204


@app.delete("/events/<int:event_id>")
def delete_event(event_id):
    event = find_event(event_id)

    if event is None:
        return {"error": "Eventet findes ikke"}, 404

    events.remove(event)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
