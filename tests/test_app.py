import pytest

from main import DRINKS, app


@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def session_cookie(client):
    """Fixture to manage session cookie across tests."""
    response = client.post("/calculate")
    cookie_header = response.headers.get("Set-Cookie")
    if cookie_header:
        return cookie_header.split(";")[0]
    pytest.fail("Failed to initialize session cookie")


def set_cookie(client, session_cookie):
    """Set the session cookie for the given client."""
    if session_cookie:
        key, value = session_cookie.split("=")
        client.set_cookie(key, value)


def test_index_page(client):
    """Test loading of the index page."""
    response = client.get("/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert b"Promillerechner" in response.data, "Text 'Promillerechner' missing"


def test_add_drink(client, session_cookie):
    """Test adding a drink."""
    set_cookie(client, session_cookie)
    response = client.post("/add_drink", data={"drink": "Bier (1000ml, 6%)"})
    assert response.status_code == 302, f"Expected 302, got {response.status_code}"


def test_use_session_cookie(client, session_cookie):
    """Test using the session cookie to maintain state."""
    set_cookie(client, session_cookie)
    response = client.get("/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert b"Promillerechner" in response.data, "Session data not maintained"


def test_add_custom_drink(client, session_cookie):
    """Test adding a custom drink."""
    set_cookie(client, session_cookie)
    response = client.post(
        "/add_custom_drink",
        data={
            "custom-drink-name": "Custom Beer",
            "custom-drink-alcohol": "5",
            "custom-drink-volume": "500",
            "custom-drink-unit": "ml",
        },
    )
    assert response.status_code == 302, f"Expected 302, got {response.status_code}"
    assert b"Custom Beer" in client.get("/").data, "Custom Beer not added"


def test_remove_drink(client, session_cookie):
    """Test removing a drink."""
    set_cookie(client, session_cookie)
    drink_name = str(DRINKS[0])
    client.post("/add_drink", data={"drink": drink_name})

    first_history = client.get("/history")
    assert drink_name.encode() in first_history.data, "Drink not added to history"

    remove_response = client.post("/remove_drink", data={"drink": drink_name})
    assert remove_response.status_code in [
        200,
        302,
    ], f"Got {remove_response.status_code}"

    second_history = client.get("/history")
    assert drink_name.encode() not in second_history.data, "Drink still in history"


def test_calculate_bac(client, session_cookie):
    """Test BAC calculation."""
    set_cookie(client, session_cookie)
    client.post("/add_drink", data={"drink": str(DRINKS[0])})
    response = client.post(
        "/calculate", data={"weight": "70", "gender": "male", "age": "25"}
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert b"BAC" in response.data
    assert b"1.046 Promille" in response.data
    assert b"7.01 Stunden" in response.data


def test_reset(client, session_cookie):
    """Test resetting the history."""
    set_cookie(client, session_cookie)
    client.post("/add_drink", data={"drink": str(DRINKS[0])})
    client.post("/add_drink", data={"drink": str(DRINKS[2])})

    history = client.get("/history")
    client.get("/reset")
    response = client.get("/history")

    assert history.data != response.data, "History not reset"
    assert "Noch keine Getränke hinzugefügt." in response.text


def test_history(client, session_cookie):
    """Test viewing the history."""
    set_cookie(client, session_cookie)
    client.post("/add_drink", data={"drink": str(DRINKS[0])})
    client.post("/add_drink", data={"drink": str(DRINKS[2])})
    response = client.get("/history")

    assert str(DRINKS[0]) in response.data.decode()
    assert str(DRINKS[2]) in response.data.decode()


def test_reset_history(client, session_cookie):
    """Test resetting with specific endpoint."""
    set_cookie(client, session_cookie)
    client.get("/history/reset")
    response = client.get("/history")
    assert "Noch keine Getränke hinzugefügt." in response.text


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health-check")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.data == b"OK", f"Expected 'OK', got {response.data}"


def test_remove_history_entry(client, session_cookie):
    """Test removing a drink entry from history."""

    set_cookie(client, session_cookie)

    client.get("/history/reset")
    drink_to_add = str(DRINKS[4])
    client.post("/add_drink", data={"drink": drink_to_add})

    history_response = client.get("/history")
    assert drink_to_add in history_response.text, "Drink was not added to history"

    german_time = extract_time_from_history(history_response, drink_to_add)

    remove_drink_entry(client, drink_to_add, german_time)
    verify_removal(client, drink_to_add)


def extract_time_from_history(history_response, drink_to_add):
    """Extract the time associated with a drink entry in the history using split."""
    html_drink_start = history_response.text.find(
        f'<span class="highlight">{drink_to_add}'
    )
    assert html_drink_start != -1, "Drink entry not found in history"

    html_snippet = history_response.text[html_drink_start : html_drink_start + 200]

    try:
        time_marker = html_snippet.split('<span class="entry-time">')[1].split(
            "</span>"
        )[0]
    except IndexError:
        raise AssertionError("Time marker not found for the drink entry")

    return time_marker.strip()


def remove_drink_entry(client, drink_to_add, german_time):
    """Remove a drink entry from history."""
    remove_response = client.post(
        "/history/remove", data={"drink": drink_to_add, "time": german_time}
    )
    assert (
        remove_response.status_code == 302
    ), f"Expected 302, got {remove_response.status_code}"


def verify_removal(client, drink_to_add):
    """Verify that a drink entry has been removed from history."""
    updated_history = client.get("/history")
    assert drink_to_add not in updated_history.data.decode(), "Drink not removed"


def test_calculate_no_drinks(client, session_cookie):
    """Test BAC calculation with no drinks."""
    set_cookie(client, session_cookie)

    response = client.post(
        "/calculate", data={"weight": "70", "gender": "male", "age": "25"}
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert (
        b"No drinks selected." in response.data
    ), "Expected no drinks selected message"


def test_calculate_bac_with_drinks(client, session_cookie):
    """Test BAC calculation with drinks added."""
    set_cookie(client, session_cookie)
    client.post("/add_drink", data={"drink": str(DRINKS[0])})

    response = client.post(
        "/calculate", data={"weight": "70", "gender": "male", "age": "25"}
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert b"BAC" in response.data, "Expected BAC result in response"
    assert b"Promille" in response.data, "Expected Promille in response"
    assert b"Stunden" in response.data, "Expected hours to sober in response"
