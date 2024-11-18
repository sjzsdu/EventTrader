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
    
    
def is_stock_or_index(stock_code):
    """
    判断给定的股票编码是个股还是指数

    :param stock_code: str, 股票编码
    :return: str, 'stock' 或 'index'
    """

    # 确保股票代码是字符串
    stock_code = str(stock_code)

    # 判断当前市场的股票编码规则
    if stock_code.isdigit():
        # 纯数字的编码
        if len(stock_code) == 6:
            if stock_code.startswith(('000', '001', '002', '300', '600', '601', '603', '688')):
                return 'stock'
            elif stock_code.startswith(('0000', '0001', '0009', '399')):
                return 'index'
        # 沪深交易所指数通常以000或399开头并且是四位或六位
        elif len(stock_code) <= 4:
            return 'index'
    else:
        # 字母开头的通常是指数，例如上证指数 'SH000001'
        if stock_code.upper().startswith(('SH', 'SZ')):
            if stock_code[2:].isdigit():
                return 'index'

    return 'unknown'

def is_stock(stock_code):
    """
    判断给定的股票编码是否是个股
    :param stock_code: str, 股票编码
    :return: bool, True 表示是个股，False 表示是指数
    """
    return is_stock_or_index(stock_code) == 'stock'

def is_index(stock_code):
    """
    判断给定的股票编码是否是指数
    :param stock_code: str, 股票编码
    :return: bool, True 表示是指数，False 表示是个股
    """
    return is_stock_or_index(stock_code) =='index'