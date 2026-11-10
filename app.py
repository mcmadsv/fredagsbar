
import os

import httpx
import streamlit as st


API_URL = os.environ.get("API_URL", "http://127.0.0.1:5000")


def api_request(method, path, data=None):
    try:
        response = httpx.request(
            method,
            f"{API_URL}{path}",
            json=data,
            timeout=2
        )
        response.raise_for_status()

        if response.status_code == 204:
            return True

        return response.json()

    except httpx.ConnectError:
        st.error("Kan ikke forbinde til API'en. Er Flask-serveren startet?")

    except httpx.TimeoutException:
        st.error("API'en svarer for langsomt. Prøv igen.")

    except httpx.HTTPStatusError as error:
        try:
            message = error.response.json().get("error", "Ukendt fejl")
        except ValueError:
            message = "API'en returnerede en fejl"

        st.error(message)

    except (httpx.RequestError, ValueError):
        st.error("Der opstod en fejl ved kommunikationen med API'en.")

    return None


st.title("Fredagsbarens event-system")

if "name" not in st.session_state:
    st.session_state.name = ""

if "success_message" in st.session_state:
    st.success(st.session_state.pop("success_message"))

st.sidebar.header("Mit navn")
st.sidebar.text_input("Skriv dit navn", key="name")

st.header("Kommende events")

events = api_request("GET", "/events")

if events is None:
    st.stop()

overview = []

for event in events:
    overview.append({
        "Titel": event["title"],
        "Dato": event["date"],
        "Antal tilmeldte": len(event["participants"]),
        "Ledige pladser": event["capacity"] - len(event["participants"])
    })

st.dataframe(overview, use_container_width=True)

st.header("Tilmeld eller afmeld")

if events:
    event_options = {
        f'{event["title"]} (ID: {event["id"]})': event
        for event in events
    }

    selected_title = st.selectbox(
        "Vælg et event",
        list(event_options.keys())
    )

    selected_event = event_options[selected_title]

    st.write("Deltagere:", ", ".join(selected_event["participants"]) or "Ingen endnu")

    available = selected_event["capacity"] - len(selected_event["participants"])

    st.write(f"Ledige pladser: {available}")

    name = st.session_state.name.strip()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Tilmeld", disabled=available == 0):
            if not name:
                st.error("Du skal skrive dit navn i sidebaren.")
            else:
                result = api_request(
                    "POST",
                    f'/events/{selected_event["id"]}/signups',
                    {"name": name}
                )

                if result is not None:
                    st.session_state.success_message = "Du er nu tilmeldt!"
                    st.rerun()

    with col2:
        if st.button("Afmeld"):
            if not name:
                st.error("Du skal skrive dit navn i sidebaren.")
            else:
                result = api_request(
                    "DELETE",
                    f'/events/{selected_event["id"]}/signups/{name}'
                )

                if result is not None:
                    st.session_state.success_message = "Du er nu afmeldt!"
                    st.rerun()
else:
    st.info("Der er ingen events endnu.")


st.header("Opret nyt event")

with st.form("create_event"):
    title = st.text_input("Titel")
    date = st.date_input("Dato")
    capacity = st.number_input("Antal pladser", min_value=1, step=1)

    submitted = st.form_submit_button("Opret event")

    if submitted:
        if not title.strip():
            st.error("Du skal skrive en titel.")
        else:
            new_event = {
                "title": title.strip(),
                "date": date.isoformat(),
                "capacity": int(capacity)
            }

            result = api_request("POST", "/events", new_event)

            if result is not None:
                st.session_state.success_message = "Eventet blev oprettet!"
                st.rerun()
