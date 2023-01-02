def get_diet_aggregate(user_items: list) -> dict:
    """
    Returns the total number of distinct items and the total calories of the given list of
    items.
    """
    item_count = len(user_items)
    calorie_count = 0
    for user_item in user_items:
        calorie_count += user_item.total_calories

    return {"item_count": item_count, "calorie_count": calorie_count}
