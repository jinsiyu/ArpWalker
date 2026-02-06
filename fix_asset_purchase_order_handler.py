import os
import sys
import time

import uuid

from PySide6.QtWidgets import QApplication
from path import Path
from selenium.webdriver.common.by import By

from download_directory_utils import create_download_dir, change_download_dir
from edge_scraper import EdgeScraper
from ciomp_scraper import demonstrate_ciomp_login_process
from form_handler import handle_form_page
from loan_handler import handle_loan_page
from modify_report_name import modify_report_name


def handle_fix_asset_purchase_order_page(scraper, timeout=5):
    """
    处理耗材采购单网页的方法

    Args:
        scraper: EdgeScraper实例
        timeout: 等待对话框的超时时间（秒）

    Returns:
        bool: 如果是耗材采购单并成功处理则返回True，否则返回False
    """
    try:
        loan_number_texts = []

        # 查找申请单号元素
        purchase_order_number_elements = scraper.find_elements(By.XPATH, "//label[text()='申请单号']", timeout)
        if purchase_order_number_elements:
            purchase_order_number_div = scraper.find_element(By.XPATH, "//label[text()='申请单号']/following-sibling::div[1]")
            purchase_order_number_text = purchase_order_number_div.text.strip()
            print(f"已获取申请单号元素:{purchase_order_number_text}")
        else:
            purchase_order_number_text = ""
            print("未找到申请单号元素")

        # 查找借款单号元素
        loan_number_list = scraper.find_elements(By.XPATH, '''//span[text()='单号' and @class="text-field p-l-sm"]/following-sibling::span[1]''', timeout)
        print(f"找到 {len(loan_number_list)} 个借款单号:")
        for i, loan_label in enumerate(loan_number_list):
            loan_number_text = loan_label.text.strip()
            loan_number_texts.append(loan_number_text)
            print(f"已获取第{i + 1}个借款单号元素:{loan_number_text}")

        # 检查当前工作目录下是否有包含采购订单号的文件夹
        existing_folder = None
        if purchase_order_number_text:
            for item in os.listdir('.'):
                if os.path.isdir(item) and purchase_order_number_text in item:
                    existing_folder = Path(item)
                    break

        if existing_folder:
            download_dir = existing_folder
            print(f"找到包含资产采购单号的现有文件夹: {download_dir.absolute()}")
        else:
            # 构建包含所有单号的文件夹名
            folder_parts = []
            if purchase_order_number_text:
                folder_parts.append(purchase_order_number_text)
            if loan_number_texts:
                # 添加所有借款单号
                folder_parts.extend([ln for ln in loan_number_texts if ln])

            # 如果有至少一个单号，使用它们构建文件夹名，否则使用UUID
            if folder_parts:
                folder_name = "_".join(folder_parts)
                download_dir = Path(f"./{folder_name}")
                print(f"使用所有单号连接作为下载目录: {folder_name}")
            else:
                # 使用UUID作为文件夹名
                unique_id = str(uuid.uuid4())
                download_dir = Path(f"./{unique_id}")
                print(f"使用UUID作为下载目录: {unique_id}")
            # 创建下载目录
            create_download_dir(download_dir)
        # 设置浏览器下载路径
        change_download_dir(download_dir, scraper)

        # 点击更多元素
        more_list = scraper.find_elements(By.XPATH, "//span[text()='更多']")
        print(f"找到 {len(more_list)} 个更多:")
        for i, link in enumerate(more_list):
            # 点击打印封面元素
            link.click()
            print(f"已点击第{i + 1}个更多元素")
            time.sleep(1)

        # 点击下载按钮元素
        download_button_list = scraper.find_elements(By.XPATH, '''//i[@class="ci-download m-r text-xlg text-primary sslab-mr-xs"]''')
        print(f"找到 {len(download_button_list)} 个下载按钮:")
        for i, download_button in enumerate(download_button_list):
            scraper.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_button)
            time.sleep(3)
            download_button.click()
            print(f"已点击第{i + 1}个下载按钮元素")

        # 点击操作元素
        span_list = scraper.find_elements(By.XPATH, "//span[text()='操作']", timeout)
        print(f"找到 {len(span_list)} 个操作:")
        for i, link in enumerate(span_list):
            text = link.text.strip()
            print(f"{i + 1}. {text}")
            if link.text == "操作":
                # 点击打印封面元素
                link.click()
                print(f"已点击第{i + 1}个操作元素")
                time.sleep(1)
                break

        # 点击报表打印元素
        a_list = scraper.find_elements(By.XPATH, "//a[text()='报表打印']", timeout)
        print(f"找到 {len(a_list)} 个报表打印:")
        for i, link in enumerate(a_list):
            text = link.text.strip()
            print(f"{i + 1}. {text}")
            if link.text == "报表打印":
                # 点击入库验收单打印元素
                link.click()
                print(f"已点击第{i + 1}个报表打印元素")
                break

        handle_form_page(scraper, timeout)

        # 点击借款单号元素
        print(f"找到 {len(loan_number_list)} 个借款单号:")
        for i, link in enumerate(loan_number_list):
            loan_number_span = scraper.wait_and_click(By.XPATH, '''(//span[text()='单号' and @class="text-field p-l-sm"]/following-sibling::span[1])''' + f"[{i + 1}]")
            print(f"已点击第{i + 1}个借款单号元素")
            time.sleep(timeout)
            handle_loan_page(scraper, download_dir, timeout)
            # 完成后执行浏览器后退操作
            scraper.driver.back()
            print(f"已执行浏览器后退操作")
            time.sleep(timeout)

        # 获取采购单号并重命名下载的PDF文件
        if purchase_order_number_text:
            modify_report_name(download_dir, "AM_ASSETS_PURCHASE_ORDER.pdf", f"资产采购单号{purchase_order_number_text}.pdf")

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
        "当前页面是否为资产采购单页？"
    )

    if user_confirmed:
    # 用户点击了"是"，认为当前页面是资产采购单页
        print("用户确认当前页面为资产采购单页")
        handle_fix_asset_purchase_order_page(scraper)
    else:
        # 用户点击了"否"或关闭了对话框
        print("用户取消操作或认为当前页面不是资产采购单页")

        # 显示确认弹窗
    user_confirmed = scraper.wait_for_user_interaction(
        "请确认操作已完成，然后点击确定继续。"
    )

    # 关闭浏览器
    try:
        scraper.close()
    except:
        print("浏览器可能已关闭")

    # 如果用户知道登录后的特定页面URL，可以调用以下函数
    # access_known_post_login_page("https://arp.ciomp.ac.cn/specific-page")


if __name__ == "__main__":
    main()