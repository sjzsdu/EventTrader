def friendly_number(number, decimal_places=2):
    """
    将一个数值转换为比较友好的格式，用亿和万为单位，并支持指定小数点位数。

    :param number: 需要转换的数值
    :param decimal_places: 小数点位数，默认为2
    :return: 转换后的字符串
    """
    if number is None:
        return "无效的数字"

    try:
        num = float(number)
    except (ValueError, TypeError):
        return "无效的数字"

    if num >= 1e8:  # 大于等于 1 亿
        return f"{num / 1e8:.{decimal_places}f} 亿"
    elif num >= 1e4:  # 大于等于 1 万
        return f"{num / 1e4:.{decimal_places}f} 万"
    else:
        return f"{num:.{decimal_places}f}"

def get_first_line(text):
    # 使用 splitlines() 分割字符串，然后使用列表解析去除每行首尾空格并过滤掉空行
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    # 返回第一行，如果没有有效行则返回空字符串
    return lines[0] if lines else ''
    
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

import pandas as pd
import matplotlib.pyplot as plt
def plot_line_chart(df: pd.DataFrame, columns: list[str], title='Line Chart', ylabel='Y-axis', figsize=(10, 6)):
    """
    绘制折线图的函数。

    参数:
    - df: Pandas DataFrame，包含数据的DataFrame。
    - x_column: str, 用作x轴的列名。
    - y_columns: list of str, 用作y轴的列名列表。
    - title: str, 图表的标题。
    - xlabel: str, x轴的标签。
    - ylabel: str, y轴的标签。
    - figsize: tuple, 图表的大小。

    返回:
    - None
    """
    df['日期'] = pd.to_datetime(df['日期'])
    plt.figure(figsize=figsize)
    for column in columns:
        plt.plot(df['日期'], df[column], label=column)

    # 添加标题和标签
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(ylabel)

    plt.xticks(rotation=45)
    plt.legend()

    # 显示图形
    plt.tight_layout()
    plt.show()