import pytest


# Fixtures for api_client

@pytest.fixture
def mock_response_success():
    class MockResponse:
        status_code = 200

        def json(self):
            return {"success": True, "data": 123}

        def raise_for_status(self):
            pass

        text = '{"success": true, "data": 123}'

    return MockResponse()


@pytest.fixture
def mock_response_invalid_json():
    class MockResponse:
        status_code = 200

        def json(self):
            raise ValueError("Invalid JSON")

        def raise_for_status(self):
            pass

        text = "<<<invalid>>>"

    return MockResponse()
