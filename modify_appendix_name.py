import urllib.parse
import os

def modify_appendix_name(url, new_name):
    """
    修改URL中appendix_name参数的值，保留文件扩展名
    
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
        
        # 创建新的文件名，保留扩展名
        new_filename = new_name + ext
        
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

def extract_original_filename_from_url(url):
    """
    从URL中提取原始的appendix_name参数值
    
    Args:
        url (str): 原始URL
    
    Returns:
        str: 原始文件名
    """
    parsed_url = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
    
    if 'appendix_name' in params:
        return params['appendix_name'][0]
    
    return None

def extract_actual_filename_from_url(url):
    """
    从URL中提取实际的文件名（用于验证目的）
    
    Args:
        url (str): 修改后的URL
    
    Returns:
        str: 提取到的文件名
    """
    parsed_url = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
    
    if 'appendix_name' in params:
        return params['appendix_name'][0]
    
    # 如果没有appendix_name参数，则尝试从路径中获取文件名
    path_parts = parsed_url.path.split('/')
    if path_parts:
        filename = path_parts[-1]
        if '.' in filename:  # 检查是否为文件
            return filename
    
    return "unknown_file"

# 示例使用
if __name__ == "__main__":
    original_url = "https://arp.ciomp.ac.cn/service2/appendix!thumbnail?_t=OTQwMURCNEFGQzFG&_c=1b3992b645a775bf3883ed3c4a35bb73&_m=100802&appendix_url=appendix/M00/9C/92/rB9kjWhcpvCAA08FAEPvlSHZagQ752.png&appendix_name=%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_2025-06-26_094607_986.png&thumb_type=scale&thumb_scale=0.5"
    
    print("原始URL:")
    print(original_url)
    
    modified_url = modify_appendix_name(original_url, "test")
    print("\n修改后的URL:")
    print(modified_url)
    
    actual_filename = extract_actual_filename_from_url(modified_url)
    print(f"\n从修改后的URL中提取的文件名: {actual_filename}")
    
    original_filename = extract_original_filename_from_url(original_url)
    print(f"原始URL中的文件名: {original_filename}")