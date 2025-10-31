import os
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test the /health endpoint returns correct status"""
    rv = client.get('/health')
    json_data = rv.get_json()
    assert rv.status_code == 200
    assert json_data['status'] == 'ok'
    assert 'mode' in json_data

def test_mock_mode_summarize(client):
    """Test the /api/summarize endpoint in mock mode"""
    os.environ['LEG_MODE'] = 'mock'
    rv = client.post('/api/summarize', json={
        'text': 'This is a test document.'
    })
    json_data = rv.get_json()
    assert rv.status_code == 200
    assert 'summary' in json_data
    assert 'mock' in json_data['summary'].lower()

def test_missing_text_parameter(client):
    """Test error handling when 'text' parameter is missing"""
    rv = client.post('/api/summarize', json={})
    assert rv.status_code == 400
    json_data = rv.get_json()
    assert 'error' in json_data