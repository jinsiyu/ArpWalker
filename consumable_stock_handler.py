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
from modify_report_name import modify_report_name
from modify_url_appendix_name import modify_url_appendix_name
from press_download_button import press_download_button


def handle_consumable_stock_page(scraper, timeout=10):
    """
    处理耗材验收网页的方法

    Args:
        scraper: EdgeScraper实例
        timeout: 等待对话框的超时时间（秒）

    Returns:
        bool: 如果是耗材验收页并成功处理则返回True，否则返回False
    """
    try:
        # 查找验收单号元素
        stock_number_elements = scraper.find_elements(By.XPATH, "//label[text()='验收单号']", timeout)
        if stock_number_elements:
            stock_number_text = scraper.find_element(By.XPATH, "//label[text()='验收单号']/following-sibling::div[1]", timeout).text.strip()
            print(f"已获取验收单号元素:{stock_number_text}")
        else:
            stock_number_text = ""
            print("未找到验收单号元素")

        # 查找采购订单号元素
        purchase_order_number_elements = scraper.find_elements(By.XPATH, "//label[text()='采购订单号']", timeout)
        if purchase_order_number_elements:
            purchase_order_number_div = scraper.find_element(By.XPATH, "//label[text()='采购订单号']/following-sibling::div[1]", timeout)
            purchase_order_number_text = purchase_order_number_div.text.strip()
            print(f"已获取采购订单号元素:{purchase_order_number_text}")
        else:
            purchase_order_number_text = ""
            print("未找到采购订单号元素")

        # 检查当前工作目录下是否有包含入库单号的文件夹
        existing_folder = None
        if stock_number_text:
            for item in os.listdir('.'):
                if os.path.isdir(item) and stock_number_text in item:
                    existing_folder = Path(item)
                    break
        
        if existing_folder:
            download_dir = existing_folder
            print(f"找到包含入库单号的现有文件夹: {download_dir.absolute()}")
        else:
            # 构建包含所有单号的文件夹名
            folder_parts = []
            if purchase_order_number_text:
                folder_parts.append(purchase_order_number_text)
            if stock_number_text:
                folder_parts.append(stock_number_text)

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
        press_download_button(scraper)

        # 点击更多元素
        a_list = scraper.find_elements(By.XPATH, "//a[text()='更多']", timeout)
        print(f"找到 {len(a_list)} 个更多:")
        for i, link in enumerate(a_list):
            text = link.text.strip()
            print(f"{i + 1}. {text}")
            if link.text == "更多":
                # 点击更多元素
                link.click()
                print(f"已点击第{i + 1}个更多元素")
                time.sleep(1)
                break

        # 点击入库验收单打印元素
        a_list = scraper.find_elements(By.XPATH, "//a[text()='入库验收单打印']", timeout)
        print(f"找到 {len(a_list)} 个入库验收单打印:")
        for i, link in enumerate(a_list):
            text = link.text.strip()
            print(f"{i + 1}. {text}")
            if link.text == "入库验收单打印":
                # 点击入库验收单打印元素
                link.click()
                print(f"已点击第{i + 1}个入库验收单打印元素")
                break
        handle_form_page(scraper, timeout)

        # 点击更多元素
        a_list = scraper.find_elements(By.XPATH, "//a[text()='更多']", timeout)
        print(f"找到 {len(a_list)} 个更多:")
        for i, link in enumerate(a_list):
            text = link.text.strip()
            print(f"{i + 1}. {text}")
            if link.text == "更多":
                # 点击更多元素
                link.click()
                print(f"已点击第{i + 1}个更多元素")
                time.sleep(1)
                break

        # 点击入库领用单打印元素
        a_list = scraper.find_elements(By.XPATH, "//a[text()='入库领用单打印']", timeout)
        print(f"找到 {len(a_list)} 个入库领用单打印:")
        for i, link in enumerate(a_list):
            text = link.text.strip()
            print(f"{i + 1}. {text}")
            if link.text == "入库领用单打印":
                # 点击入库验收单打印元素
                link.click()
                print(f"已点击第{i + 1}个入库领用单打印元素")
                break
        handle_form_page(scraper, timeout)

        # 定位图片元素
        img_list = scraper.find_elements(By.XPATH, '''//img[@ng-repeat="img in thumbnails"]''', timeout)
        print(f"找到 {len(img_list)} 个图片:")
        for i, img in enumerate(img_list):
            img_src = img.get_attribute('src')
            print(f"第{i + 1}个大图元素:{img_src}")
            new_name = modify_url_appendix_name(img_src, f"耗材图片_{i + 1}")

            scraper.driver.get(new_name)
            time.sleep(1)

        mat_detail = scraper.wait_and_click(By.XPATH, '''//span[@ng-click="openMaterialDetail(item.ID,'full')"]''', timeout)
        print(f"已点击耗材详情元素")
        # 查找领用单号元素
        out_number_div = scraper.find_element(By.XPATH, "//label[text()='领用单号']/following-sibling::div[1]", timeout)
        out_number_text = out_number_div.text.strip()
        print(f"已获取领用单号元素:{out_number_text}")

        # 获取验收单号并重命名下载的PDF文件
        if stock_number_text:
            modify_report_name(download_dir, "AM_MAT_ACPT.pdf", f"耗材验收单号{stock_number_text}.pdf")

        # 获取领用单号并重命名下载的PDF文件
        if out_number_text:
            modify_report_name(download_dir, "AM_MAT_STOCK_IN.pdf", f"耗材领用单号{out_number_text}.pdf")

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
        "当前页面是否为耗材验收页？"
    )

    if user_confirmed:
    # 用户点击了"是"，认为当前页面是耗材验收页
        print("用户确认当前页面为耗材验收页")
        handle_consumable_stock_page(scraper)
    else:
        # 用户点击了"否"或关闭了对话框
        print("用户取消操作或认为当前页面不是耗材验收页")

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