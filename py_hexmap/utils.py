def get_field_display_string(field):
    """
    Converts a complex Field object into a simple string representation of its estate for display.
    """
    if(str(field.type)=="water"):
        return "water"
    elif(field.capital != -1):
        return field.town_name
    elif(field.estate  =="" ):
        return "land"
    elif(field.estate == "town"):
        return field.town_name
    else:
        return field.estate

def field_to_dict(field):
    """
    Converts a Field object into a dictionary representation.
    """
    return {
        "f_x": field.f_x,
        "f_y": field.f_y,
        "x": field.x,
        "y": field.y,
        "land_id": field.land_id,
        "type": field.type,
        "capital": field.capital,
        "is_land": field.is_land,
        "estate": field.estate,
        "town_name": field.town_name,
        "display_estate": get_field_display_string(field)
    }

def fields_to_dict_representation(fields, x_max: int, y_max: int):
    """
    Converts the dictionary of Field objects into a dictionary where keys are field keys
    and values are dictionary representations of the fields.
    This function is essential for creating the final, easily serializable
    JSON output from the internal map representation.

    Args:
        fields (dict): A dictionary of Field objects.
        x_max (int): The maximum X-coordinate for the map (width).
        y_max (int): The maximum Y-coordinate for the map (height).
    """
    output = {}
    for x in range(x_max):
        for y in range(y_max):
            key = "f" + str(x) + "x" + str(y)
            output[key] = field_to_dict(fields[key])
    return output