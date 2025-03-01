from typing import List
from operator import itemgetter
from src.repositories import DTOType


def sort_dto_list_order_by(
    dto: DTOType, dto_list: List[DTOType], order_by: str
) -> List[DTOType]:
    """
    Sorts a list of DTOs by a given field.

    :param dto: DTO class
    :param dto_list: list of DTOs
    :param order_by: field to sort by
    :return: sorted list of DTOs
    """
    dict_list = [dto.model_dump(dto_) for dto_ in dto_list]
    sorted_list = sorted(dict_list, key=itemgetter(order_by))
    return [dto(**item) for item in sorted_list]
