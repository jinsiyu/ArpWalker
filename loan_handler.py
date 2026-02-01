import os
import shutil
import time

import uuid
from path import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # 用于定义等待条件
from selenium.webdriver.support.wait import WebDriverWait

from download_directory_utils import create_download_dir, change_download_dir
from edge_scraper import EdgeScraper
from ciomp_scraper import demonstrate_ciomp_login_process
from form_handler import handle_form_page


def handle_loan_page(scraper, download_dir = None, timeout=5):
    """
    处理耗材采购单网页的方法

    Args:
        scraper: EdgeScraper实例
        download_dir: 下载地址
        timeout: 等待对话框的超时时间（秒）

    Returns:
        bool: 如果是耗材采购单并成功处理则返回True，否则返回False
    """
    try:
        # 查找凭证号元素
        voucher_span = scraper.find_element(By.XPATH, "//span[text()='凭证号']/following-sibling::span[1]", timeout)
        voucher_text = voucher_span.text.strip()
        print(f"已获取凭证号元素:{voucher_text}")

        # 查找采购订单号元素
        loan_label = scraper.find_element(By.XPATH, "//label[text()='借款单号']/following-sibling::div[1]", timeout)
        loan_text = loan_label.text.strip()
        print(f"已获取借款单号元素:{loan_text}")

        if download_dir is None:
            #检查当前工作目录下是否有包含采购订单号的文件夹
            existing_folder = None
            if loan_text:
                for item in os.listdir('.'):
                    if os.path.isdir(item) and loan_text in item:
                        existing_folder = Path(item)
                        break

            if existing_folder:
                download_dir = existing_folder
                print(f"找到包含借款单号的现有文件夹: {download_dir.absolute()}")
            else:
                # 如果有单号，使用它们构建文件夹名，否则使用UUID
                if loan_text:
                    folder_name = loan_text
                    download_dir = Path(f"./{folder_name}")
                    print(f"使用借款单号作为下载目录: {folder_name}")
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

        # 点击更多元素
        a_list = scraper.find_elements(By.XPATH, "//a[text()='更多']", timeout)
        print(f"找到 {len(a_list)} 个更多:")
        for i, link in enumerate(a_list):
            text = link.text.strip()
            print(f"{i + 1}. {text}")
            if link.text == "更多":
                # 点击打印封面元素
                link.click()
                print(f"已点击第{i + 1}个更多元素")
                time.sleep(1)
                break

        # 点击打印封面元素
        a_list = scraper.find_elements(By.XPATH, "//a[text()='打印封面']", timeout)
        print(f"找到 {len(a_list)} 个打印封面:")
        for i, link in enumerate(a_list):
            text = link.text.strip()
            print(f"{i + 1}. {text}")
            if link.text == "打印封面":
                # 点打印封面元素
                link.click()
                print(f"已点击第{i + 1}个打印封面元素")
                break

        handle_form_page(scraper, timeout)

        if voucher_text:
            voucher_span.click()
            # 点击打印封面元素
            print_a = scraper.wait_and_click(By.XPATH, '''//a[text()='打印' and @class="btn btn-bar-header"]''', timeout)
            print(f"已点击打印元素")
            handle_form_page(scraper, timeout)
            # 完成后执行浏览器后退操作
            scraper.driver.back()
            print(f"已执行浏览器后退操作")


        # 获取借款单号并重命名下载的PDF文件
        if loan_text:
            old_pdf_path = download_dir / "FM_LOAN_RPT.pdf"
            new_pdf_path = download_dir / f"借款单号{loan_text}.pdf"
            
            # 等待文件下载完成
            max_wait_time = 30  # 最多等待30秒
            wait_count = 0

            while not old_pdf_path.exists() and wait_count < max_wait_time:
                time.sleep(1)
                wait_count += 1
            
            # 检查目标文件是否已存在，如果存在则添加序号
            counter = 1
            final_new_path = new_pdf_path
            while final_new_path.exists():
                name_part = new_pdf_path.stem
                ext_part = new_pdf_path.suffix
                final_new_path = download_dir / f"{name_part}({counter}){ext_part}"
                counter += 1
            
            if old_pdf_path.exists():
                old_pdf_path.rename(final_new_path)
                if final_new_path != new_pdf_path:
                    print(f"已将 FM_LOAN_RPT.pdf 重命名为 {final_new_path.name} (原名称 {new_pdf_path.name} 已存在，使用新名称)")
                else:
                    print(f"已将 FM_LOAN_RPT.pdf 重命名为 {final_new_path.name}")
            else:
                print(f"警告: 未找到 FM_LOAN_RPT.pdf 文件，可能下载失败或名称不同")


        # 获取凭证号并重命名下载的PDF文件
        if voucher_text:
            old_pdf_path = download_dir / "FM_VOUCHER_INFO.pdf"
            new_pdf_path = download_dir / f"借款凭证号{voucher_text}.pdf"
            
            # 等待文件下载完成
            max_wait_time = 30  # 最多等待30秒
            wait_count = 0
            while not old_pdf_path.exists() and wait_count < max_wait_time:
                time.sleep(1)
                wait_count += 1
            

            # 检查目标文件是否已存在，如果存在则添加序号
            counter = 1
            final_new_path = new_pdf_path
            while final_new_path.exists():
                name_part = new_pdf_path.stem
                ext_part = new_pdf_path.suffix
                final_new_path = download_dir / f"{name_part}({counter}){ext_part}"
                counter += 1
            
            if old_pdf_path.exists():
                old_pdf_path.rename(final_new_path)
                if final_new_path != new_pdf_path:
                    print(f"已将 FM_VOUCHER_INFO.pdf 重命名为 {final_new_path.name} (原名称 {new_pdf_path.name} 已存在，使用新名称)")
                else:
                    print(f"已将 FM_VOUCHER_INFO.pdf 重命名为 {final_new_path.name}")
            else:
                print(f"警告: 未找到 FM_VOUCHER_INFO.pdf 文件，可能下载失败或名称不同")

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
    # 显示确认弹窗
    user_confirmed = scraper.wait_for_user_interaction(
        "当前页面是否为借款单页？"
    )

    if user_confirmed:
    # 用户点击了"是"，认为当前页面是借款单页
        print("用户确认当前页面为借款单页")
        handle_loan_page(scraper)
    else:
        # 用户点击了"否"或关闭了对话框
        print("用户取消操作或认为当前页面不是借款单页")

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