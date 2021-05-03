import json


def test_create_short_code(test_client):
    data = {
        "url": "http://test.test",
        "shortcode": "6ty7y6"
    }
    response = test_client.post("/create_short_url",
               headers={"Content-Type": "application/json"},
               data=json.dumps(data),
             )
    assert response.status_code == 201


def test_url_present_or_not(test_client):
    data = {
        "shortcode": "test34"
    }
    response = test_client.post("/create_short_url",
                                headers={"Content-Type": "application/json"},
                                data=json.dumps(data),
                                )
    assert response.status_code == 400


def test_invalid_short_code(test_client):
    data = {
        "url": "http://test.com",
        "shortcode": "test34))"
    }
    response = test_client.post("/create_short_url",
                                headers={"Content-Type": "application/json"},
                                data=json.dumps(data),
                                )
    assert response.status_code == 404


def test_invalid_length_short_code(test_client):
    data = {
        "url": "http://test.com",
        "shortcode": "test3498uytrer"
    }
    response = test_client.post("/create_short_url",
                                headers={"Content-Type": "application/json"},
                                data=json.dumps(data),
                                )
    assert response.status_code == 404


def test_short_code_exists_or_not(test_client):
    response = test_client.get('/ty56ty_))')
    assert response.status_code == 404


def test_stats_short_code(test_client):
    response = test_client.get('/ui7890__))')
    assert response.status_code == 404






