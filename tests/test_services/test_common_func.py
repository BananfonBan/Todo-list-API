import pytest
from src.services.common_func import sort_dto_list_order_by
from src.dto import UserResponseDTO


def test_sort_dto_list_order_by():
    test_data = [
        UserResponseDTO(id=2, name="Bob", email="email1@test.com"),
        UserResponseDTO(id=1, name="Alice", email="email2@test.com"),
        UserResponseDTO(id=3, name="Charlie", email="email3@test.com"),
    ]

    sorted_by_id = sort_dto_list_order_by(UserResponseDTO, test_data, "id")
    assert [item.id for item in sorted_by_id] == [1, 2, 3]

    sorted_by_name = sort_dto_list_order_by(UserResponseDTO, test_data, "name")
    assert [item.name for item in sorted_by_name] == ["Alice", "Bob", "Charlie"]

    sorted_by_age = sort_dto_list_order_by(UserResponseDTO, test_data, "email")
    assert [item.email for item in sorted_by_age] == [
        "email1@test.com",
        "email2@test.com",
        "email3@test.com",
    ]


def test_sort_dto_list_order_by_empty_list():
    empty_list = []
    result = sort_dto_list_order_by(UserResponseDTO, empty_list, "id")
    assert result == []


def test_sort_dto_list_order_by_invalid_field():
    test_data = [
        UserResponseDTO(id=1, name="Alice", email="email3@test.com"),
        UserResponseDTO(id=2, name="Bob", email="email2@test.com"),
    ]

    with pytest.raises(KeyError):
        sort_dto_list_order_by(UserResponseDTO, test_data, "invalid_field")
