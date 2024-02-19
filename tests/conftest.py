import requests
import pytest
from dotenv import load_dotenv

@pytest.fixture(scope="session")
def init_config():
    load_dotenv()
    base_url = 'http://localhost:8000'
    client = requests.Session()
    client.verify = False
    config = {
        "base_url": base_url,
        "client": client,
    }
    return config