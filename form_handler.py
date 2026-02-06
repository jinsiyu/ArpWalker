import sys
import time

from PySide6.QtWidgets import QApplication
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from edge_scraper import EdgeScraper
from ciomp_scraper import demonstrate_ciomp_login_process
from selenium.webdriver.support import expected_conditions as EC  # 用于定义等待条件


def handle_form_page(scraper, timeout=5):
    """
    处理报表的方法
    
    Args:
        scraper: EdgeScraper实例
        timeout: 等待对话框的超时时间（秒）
    
    Returns:
        bool: 如果是报销页并成功处理则返回True，否则返回False
    """
    try:
        wait = WebDriverWait(scraper.driver, timeout)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'flowFrame')))
        # 点击保存报表按钮
        save_td = scraper.wait_and_click(By.XPATH, "//td[text()='保存报表']", timeout)
        print(f"已点击保存报表元素")

        # 点击Adobe PDF 文件...按钮
        adobe_td = scraper.wait_and_click(By.XPATH, "//td[text()='Adobe PDF 文件...']", timeout)
        print(f"已点击Adobe PDF 文件...元素")

        # 点击确定按钮
        confirm_td = scraper.wait_and_click(By.XPATH, "//td[text()='确定']", timeout)
        print(f"已点击确定元素")
        time.sleep(timeout)

        scraper.driver.switch_to.default_content()

        # 点击关闭按钮
        close_button = scraper.wait_and_click(By.CLASS_NAME, "ci-close", timeout)
        print(f"已点击关闭元素")

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
    app = QApplication(sys.argv)
    demonstrate_ciomp_login_process(scraper)
    # 显示确认弹窗
    user_confirmed = scraper.wait_for_user_interaction(
        "当前页面是否为报表页？"
    )

    if user_confirmed:
    # 用户点击了"是"，认为当前页面是报表页
        print("用户确认当前页面为报表页")
        handle_form_page(scraper)
    else:
        # 用户点击了"否"或关闭了对话框
        print("用户取消操作或认为当前页面不是报销查询页")
    # 关闭浏览器
    try:
        scraper.close()
    except:
        print("浏览器可能已关闭")


if __name__ == "__main__":
    main()