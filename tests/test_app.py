import flask
import pytest

from alcohol_calculator import app


@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client


# Variable to keep track of the session cookie across tests
session_cookie = None


def test_index_page(client):
    print("Test index page")
    response = client.get("/")
    assert response.status_code == 200
    assert b"Promillerechner" in response.data
    print("Index page loaded")


def test_add_drink(client):
    global session_cookie
    print("Test add drink")
    response = client.post("/add_drink", data={"drink": "Bier (1000ml, 6%)"})

    # Store the session cookie from the response
    session_cookie = response.headers.get("Set-Cookie").split(";")[
        0
    ]  # 'session=<value>'

    print(f"Session cookie: {session_cookie}")

    assert (
        response.status_code == 302
    ), f"Expected status code 302, got {response.status_code} instead"
    print(f"Successfully added drink. Session cookie: {session_cookie}")


def test_use_session_cookie(client):
    print("Test use session cookie")
    global session_cookie

    # Use the stored session cookie in the client for this test
    if session_cookie:
        client.set_cookie(
            key=session_cookie.split("=")[0], value=session_cookie.split("=")[1]
        )
    print(client.get_cookie("session"))
    response = client.get("/")
    print(response.headers)
    assert response.headers is not None


# def test_remove_drink(client):
#     client.post("/add_drink", data={"drink": "Bier (1000ml, 6%)"})
#     response = client.post("/remove_drink", data={"drink": "Bier (1000ml, 6%)"})
#     assert response.status_code == 302  # Redirect after removing
#     assert b"Bier removed." in client.get("/").data


# def test_add_custom_drink(client):
#     response = client.post(
#         "/add_custom_drink",
#         data={
#             "custom-drink-name": "Custom Beer",
#             "custom-drink-alcohol": "5",
#             "custom-drink-volume": "500",
#             "custom-drink-unit": "ml",
#         },
#     )
#     assert response.status_code == 302
#     assert b"Custom drink Custom Beer added." in client.get("/").data


# def test_calculate_bac(client):
#     client.post("/add_drink", data={"drink": "Bier (1000ml, 6%)"})
#     response = client.post(
#         "/calculate", data={"weight": "70", "gender": "male", "age": "25"}
#     )
#     assert response.status_code == 200
#     assert b"BAC" in response.data


# def test_reset(client):
#     client.get("/reset")
#     response = client.get("/")
#     assert b"Session reset." in response.data


# def test_history(client):
#     client.post("/add_drink", data={"drink": "Bier (1000ml, 6%)"})
#     response = client.get("/history")
#     assert b"Bier (1000ml, 6%)" in response.data


# def test_reset_history(client):
#     client.get("/history/reset")
#     response = client.get("/history")
#     assert b"History reset." in response.data


# def test_remove_history_entry(client):
#     client.post("/add_drink", data={"drink": "Bier (1000ml, 6%)"})
#     response = client.post(
#         "/history/remove",
#         data={
#             "drink": "Bier (1000ml, 6%)",
#             "time": "some_time",  # replace with actual time if needed
#         },
#     )
#     assert response.status_code == 302
#     assert b"History entry removed." in client.get("/history").data
