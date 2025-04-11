def convert_nested_strings_to_lowercase(data):
    if isinstance(data, dict):
        key_list = list(data.keys())
        for key in key_list:
            value = data[key]
            if isinstance(value, dict) or isinstance(value, list):
                convert_nested_strings_to_lowercase(value)
            elif isinstance(value, str):
                del data[key]
                data[key.lower()] = value.lower()
    elif isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, dict) or isinstance(item, list):
                convert_nested_strings_to_lowercase(item)
            elif isinstance(item, str):
                data[index] = item.lower()


def get_string_values(data):
    strings = []
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, str):
                strings.append(value)
            elif isinstance(value, dict):
                strings.extend(get_string_values(value))
    return strings
