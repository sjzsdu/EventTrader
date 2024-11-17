def friendly_number(number):
    """
    将一个数值转换为比较友好的格式，用亿和万为单位。
    
    :param number: 需要转换的数值
    :return: 转换后的字符串
    """
    if number is None:
        return "无效的数字"

    try:
        num = float(number)
    except ValueError:
        return "无效的数字"

    if num >= 1e8:  # 大于等于 1 亿
        return f"{num / 1e8:.2f} 亿"
    elif num >= 1e4:  # 大于等于 1 万
        return f"{num / 1e4:.2f} 万"
    else:
        return str(num)