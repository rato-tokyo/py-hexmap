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

def fields_to_matrix_representation(fields, x_max: int, y_max: int):
    """
    Converts the dictionary of Field objects into a 2D list (matrix) of strings.
    Each string represents the display string of the field.

    Args:
        fields (dict): A dictionary of Field objects.
        x_max (int): The maximum X-coordinate for the map (width).
        y_max (int): The maximum Y-coordinate for the map (height).
    """
    output = [["" for _ in range(y_max)] for _ in range(x_max)]
    for x in range(x_max):
        for y in range(y_max):
            key = "f" + str(x) + "x" + str(y)
            output[x][y] = get_field_display_string(fields[key])
    return output
