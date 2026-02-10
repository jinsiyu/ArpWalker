import sys
import time
import uuid
import json

from PySide6.QtWidgets import QApplication
from path import Path
from selenium.webdriver.common.by import By

from download_directory_utils import change_download_dir, create_download_dir
from edge_scraper import EdgeScraper
from ciomp_scraper import demonstrate_ciomp_login_process
from form_handler import handle_form_page
from modify_report_name import modify_report_name
from press_download_button import press_download_button


def handle_expense_page(scraper, timeout=5):
    """
    处理报销凭证网页的方法

    Args:
        scraper: EdgeScraper实例
        timeout: 等待对话框的超时时间（秒）

    Returns:
        bool: 如果是报销页并成功处理则返回True，否则返回False
    """
    try:
        loan_number_texts = []
        
        # 查找凭证号元素
        voucher_span = scraper.find_element(By.XPATH, "//label[text()='凭证号']/following-sibling::span[1]", timeout)
        voucher_text = voucher_span.text.strip()
        print(f"已获取凭证号元素:{voucher_text}")

        # 查找报销单号元素
        reimbursement_div = scraper.find_element(By.XPATH, "//label[text()='报销单号']/following-sibling::div[1]", timeout)
        reimbursement_text = reimbursement_div.text.strip()
        print(f"已获取报销单号元素:{reimbursement_text}")

        # 查找采购订单号元素
        purchase_order_number_elements = scraper.find_elements(By.XPATH, "//label[text()='采购订单号']")
        if purchase_order_number_elements:
            purchase_order_number_div = scraper.find_element(By.XPATH, "//label[text()='采购订单号']/following-sibling::div[1]")
            purchase_order_number_text = purchase_order_number_div.text.strip()
            print(f"已获取采购订单号元素:{purchase_order_number_text}")
        else:
            purchase_order_number_text = ""
            print("未找到采购订单号元素")

        # 查找入库单号元素
        stock_number_elements = scraper.find_elements(By.XPATH, "//label[text()='入库单号']")
        if stock_number_elements:
            stock_number_text = scraper.find_element(By.XPATH, "//label[text()='入库单号']/following-sibling::div[1]").text.strip()
            print(f"已获取入库单号元素:{stock_number_text}")
        else:
            stock_number_text = ""
            print("未找到入库单号元素")

        # 查找出差单号元素
        business_trip_number_elements = scraper.find_elements(By.XPATH, "//label[text()='出差单号']/following-sibling::div[1]")
        if business_trip_number_elements:
            business_trip_number_text = scraper.find_element(By.XPATH, "//label[text()='出差单号']/following-sibling::div[1]").text.strip()
            print(f"已获取出差单号元素:{business_trip_number_text}")
        else:
            business_trip_number_text = ""
            print("未找到出差单号元素")

        # 查找借款单号元素
        loan_number_list = scraper.find_elements(By.XPATH, "//label[text()='借款单号']/following-sibling::div[1]", timeout)
        print(f"找到 {len(loan_number_list)} 个借款单号:")
        for i, loan_label in enumerate(loan_number_list):
            loan_number_text = loan_label.text.strip()
            loan_number_texts.append(loan_number_text)
            print(f"已获取第{i + 1}个借款单号元素:{loan_number_text}")

        # 构建包含所有单号的文件夹名
        folder_parts = []
        if voucher_text:
            folder_parts.append(voucher_text)
        if reimbursement_text:
            folder_parts.append(reimbursement_text)
        if purchase_order_number_text:
            folder_parts.append(purchase_order_number_text)
        if stock_number_text:
            folder_parts.append(stock_number_text)
        if business_trip_number_text:
            folder_parts.append(business_trip_number_text)
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

        # 将凭证号、报销单号、采购订单号、入库单号、借款单号保存到JSON文件
        data_to_save = {}
        if voucher_text:
            data_to_save['voucher_number'] = voucher_text
        if reimbursement_text:
            data_to_save['reimbursement_number'] = reimbursement_text
        if purchase_order_number_text:
            data_to_save['purchase_order_number'] = purchase_order_number_text
        if stock_number_text:
            data_to_save['stock_number'] = stock_number_text
        if loan_number_texts:
            data_to_save['loan_numbers'] = loan_number_texts

        json_file_path = download_dir / "document_info.json"
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        print(f"文档信息已保存至: {json_file_path}")

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

        # 点击打印封面元素
        print_a1 = scraper.wait_and_click(By.XPATH, '''//a[text()='打印封面' and @class="btn btn-bar-header"]''', timeout)
        print(f"已点击打印封面元素")
        handle_form_page(scraper, timeout)

        # 获取报销单号并重命名下载的PDF文件
        if reimbursement_text:

            # 根据不同的可能的PDF文件名进行处理
            possible_pdf_names = [
                "FM_EXP_MATERIAL_RPT.pdf",
                "FM_EXP_FIXED_ASSETS_RPT.pdf",
                "FM_EXP_TRIP_RPT.pdf",
                "FM_EXP_GENERAL_BILL_RPT.pdf",
                "FM_EXP_LABOR_RPT.pdf"
            ]

            modify_report_name(download_dir, possible_pdf_names, f"报销单号{reimbursement_text}.pdf")

        if voucher_text:
            voucher_span.click()
            # 点击打印封面元素
            print_a2 = scraper.wait_and_click(By.XPATH, '''//a[text()='打印' and @class="btn btn-bar-header"]''', timeout)
            print(f"已点击打印元素")
            handle_form_page(scraper, timeout)
            # 完成后执行浏览器后退操作
            scraper.driver.back()
            print(f"已执行浏览器后退操作")

            modify_report_name(download_dir, "FM_VOUCHER_INFO.pdf", f"报销凭证号{voucher_text}.pdf")

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
        "当前页面是否为报销页？"
    )

    if user_confirmed:
    # 用户点击了"是"，认为当前页面是报销页
        print("用户确认当前页面为报销页")
        handle_expense_page(scraper)
    else:
        # 用户点击了"否"或关闭了对话框
        print("用户取消操作或认为当前页面不是报销页")

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