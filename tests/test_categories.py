from unittest.mock import MagicMock, patch

import ujson

from up.categories import get_categories


def test_get_categories():
    mock_response = MagicMock()
    mock_response.text = ujson.dumps(
        {
            "data": [
                {"id": "category-1", "attributes": {"name": "Groceries"}},
                {"id": "category-2", "attributes": {"name": "Transport"}},
                {"id": "category-3", "attributes": {"name": "Entertainment"}},
            ]
        }
    )

    with patch("up.categories.up_api") as mock_up_api:
        mock_up_api.get_endpoint_response.return_value = mock_response

        result = get_categories()

        assert len(result) == 3
        assert "category-1" in result
        assert "category-2" in result
        assert "category-3" in result
        mock_up_api.get_endpoint_response.assert_called_once()


def test_get_categories_empty_response():
    mock_response = MagicMock()
    mock_response.text = ujson.dumps({"data": []})

    with patch("up.categories.up_api") as mock_up_api:
        mock_up_api.get_endpoint_response.return_value = mock_response

        result = get_categories()

        assert len(result) == 0
        assert result == []


def test_get_categories_single_category():
    mock_response = MagicMock()
    mock_response.text = ujson.dumps({"data": [{"id": "single-category", "attributes": {"name": "Food"}}]})

    with patch("up.categories.up_api") as mock_up_api:
        mock_up_api.get_endpoint_response.return_value = mock_response

        result = get_categories()

        assert len(result) == 1
        assert result[0] == "single-category"

