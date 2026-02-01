"""
访问指定网站并等待用户交互后爬取页面信息的示例
此版本处理登录后页面跳转的常见情况
"""

from edge_scraper import EdgeScraper
from selenium.webdriver.common.by import By
import time
import json


def demonstrate_ciomp_login_process(scraper):
    """
    演示长春光机所数字平台的登录过程
    """
    print("长春光机所数字平台爬虫By萌新waka")
    print("="*50)
    
    # 步骤1: 访问登录页面
    print("步骤1: 访问登录页面...")
    
    try:
        login_url = "http://digital.ciomp.ac.cn/login?redirect=/home"
        success = scraper.navigate_to(login_url)
        if not success:
            print(f"无法访问 {login_url}")
            return
        
        print(f"已访问登录页面: {scraper.scrape_page_title()}")
        
        # 等待用户登录操作（使用PySide6弹窗）
        print("\\n等待用户登录操作...")
        user_confirmed = scraper.wait_for_user_interaction(
            "请在浏览器中完成登录操作并确保ARP网页已打开，完成后点击确定继续..."
        )
        
        if not user_confirmed:
            print("用户取消操作，退出程序")
            return
        
        # 尝试获取当前页面信息（即使窗口可能已改变）
        try:
            # 获取当前所有窗口句柄
            handles = scraper.driver.window_handles
            print(f"\\n当前窗口数量: {len(handles)}")
            
            if len(handles) > 0:
                # 切换到最新的窗口
                scraper.driver.switch_to.window(handles[-1])

            else:
                print("\\n没有检测到任何浏览器窗口")
                
        except Exception as e:
            print(f"\\n获取当前页面信息时出错: {str(e)}")
            print("这很常见，因为登录后页面可能已跳转到新域名")
        
    except Exception as e:
        print(f"执行过程中发生错误: {str(e)}")


def main():
    """
    主函数
    """
    print("长春光机所数字平台爬虫 - 登录后页面爬取")
    print("="*60)
    
    # 运行演示
    scraper = EdgeScraper(headless=False)
    demonstrate_ciomp_login_process(scraper)

    # 关闭浏览器
    try:
        scraper.close()
    except:
        print("浏览器可能已关闭")
    # 如果用户知道登录后的特定页面URL，可以调用以下函数
    # access_known_post_login_page("https://arp.ciomp.ac.cn/specific-page")


if __name__ == "__main__":
    main()