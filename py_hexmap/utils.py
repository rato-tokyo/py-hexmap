def field_to_estate(field):
    """
    Converts a complex Field object into a simple string representation.
    This is the final step in translating the generated map data into the
    simple matrix format required by the tests and for output.
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

def fields_to_matrix(fields):
    """
    Converts the dictionary of Field objects into a 2D list (matrix).
    This function is essential for creating the final, easily serializable
    JSON output from the internal map representation.
    """
    output= [["" for i in range(11)] for j in range(20)]
    for x in range(20):
        for y in range(11):
            key="f"+str(x)+"x"+str(y)
            output[x][y]=field_to_estate(fields[key])
    return output