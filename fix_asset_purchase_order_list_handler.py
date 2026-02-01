import time

from selenium.webdriver.common.by import By

from edge_scraper import EdgeScraper
from ciomp_scraper import demonstrate_ciomp_login_process
from fix_asset_purchase_order_handler import handle_fix_asset_purchase_order_page


def handle_fix_asset_purchase_order_list_page(scraper, timeout=5):
    """
    处理资产列表网页的方法
    
    Args:
        scraper: EdgeScraper实例
        timeout: 等待对话框的超时时间（秒）
    
    Returns:
        bool: 如果是资产列表并成功处理则返回True，否则返回False
    """
    try:
        # 查找页面上所有的链接
        links = scraper.find_elements(By.XPATH, "//span[text()='已办结' or text()='已审批']")
        print(f"找到 {len(links)} 个已办结或已审批:")
        for i, link in enumerate(links):
            text = link.text.strip()
            print(f"{i + 1}. {text}")
            if link.text == "已办结" or link.text == "已审批":
                # 点击已办结元素
                link.click()
                print(f"已点击第{i + 1}个已办结或已审批元素")
                time.sleep(timeout)

                handle_fix_asset_purchase_order_page(scraper, timeout)

                # 确认后执行浏览器后退操作
                scraper.driver.back()
                print(f"已执行浏览器后退操作")
                time.sleep(timeout)

        # 这里可以添加更多针对资产采购列表页的操作
        # 例如：点击查询按钮、导出按钮等
    except Exception as e:
        print(f"处理页面链接时出现异常: {e}")


def main():
    """
    主函数
    """
    print("长春光机所数字平台爬虫 - 登录后页面爬取")
    print("=" * 60)

    # 运行演示
    scraper = EdgeScraper(headless=False)
    demonstrate_ciomp_login_process(scraper)
    while scraper.wait_for_user_interaction(
        "当前页面是否为资产采购列表页？"
    ):
        # 用户点击了"是"，认为当前页面是资产采购列表页
        print("用户确认当前页面为资产采购列表页")
        # 尝试查找页面上的所有链接并输出
        handle_fix_asset_purchase_order_list_page(scraper)

    # 用户点击了"否"或关闭了对话框
    print("用户取消操作或认为当前页面不是资产采购列表页")

    # 关闭浏览器
    try:
        scraper.close()
    except:
        print("浏览器可能已关闭")

    # 如果用户知道登录后的特定页面URL，可以调用以下函数
    # access_known_post_login_page("https://arp.ciomp.ac.cn/specific-page")


if __name__ == "__main__":
    main()