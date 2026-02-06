import urllib.parse
import os

def modify_url_appendix_name(url, new_name):
    """
    修改URL中appendix_name参数的值，保留文件扩展名，并将中文文件名转换为URI编码

    Args:
        url (str): 原始URL
        new_name (str): 新的文件名（不包含扩展名）

    Returns:
        str: 修改后的URL
    """
    # 解析URL
    parsed_url = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)

    # 获取当前的appendix_name
    if 'appendix_name' in params:
        current_name = params['appendix_name'][0]

        # 分离文件名和扩展名
        name, ext = os.path.splitext(current_name)

        # 将新的文件名转换为URI编码
        encoded_new_name = urllib.parse.quote(new_name)

        # 创建新的文件名，保留扩展名
        new_filename = encoded_new_name + ext

        # 更新参数
        params['appendix_name'] = [new_filename]

    # 重构查询字符串
    new_query = urllib.parse.urlencode(params, doseq=True)

    # 重新构建URL
    new_url = urllib.parse.urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query,
        parsed_url.fragment
    ))

    return new_url