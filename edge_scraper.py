"""
使用 Selenium 控制 Microsoft Edge 浏览器的网络爬虫示例
"""

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt
import time


class EdgeScraper:
    def __init__(self, headless=False):
        """
        初始化 Edge 爬虫
        
        :param headless: 是否以无头模式运行（不显示浏览器界面）
        """
        self.driver = None
        self.setup_driver(headless)

    def setup_driver(self, headless=False):
        """
        配置 Edge 浏览器驱动
        """
        # 设置 Edge 选项
        options = Options()
        
        if headless:
            options.add_argument("--headless")  # 无头模式
            
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 最大化窗口
        options.add_argument("--start-maximized")
        
        # 尝试多种方式初始化Edge驱动
        driver_initialized = False
        
        # 方式1: 尝试使用webdriver-manager自动下载驱动
        try:
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            service = Service(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=options)
            driver_initialized = True
            print("成功使用webdriver-manager初始化Edge驱动")
        except ImportError:
            print("未找到 webdriver-manager，尝试其他初始化方式...")
        except Exception as e:
            print(f"webdriver-manager初始化失败: {str(e)}")
        
        # 如果方式1失败，尝试方式2: 直接使用系统中已安装的驱动
        if not driver_initialized:
            try:
                self.driver = webdriver.Edge(options=options)
                driver_initialized = True
                print("成功使用系统中已安装的Edge驱动")
            except Exception as e:
                print(f"直接初始化Edge驱动失败: {str(e)}")
        
        # 如果方式2也失败，尝试方式3: 使用Service指定路径
        if not driver_initialized:
            try:
                # 对于Windows系统，尝试常见的EdgeDriver位置
                import platform
                if platform.system() == "Windows":
                    # 尝试使用EdgeChromiumDriverManager离线缓存
                    try:
                        from webdriver_manager.microsoft import EdgeChromiumDriverManager
                        # 使用缓存的驱动（如果有）
                        service = Service(EdgeChromiumDriverManager(cache_valid_range=1).install())
                        self.driver = webdriver.Edge(service=service, options=options)
                        driver_initialized = True
                        print("成功使用缓存的Edge驱动")
                    except Exception:
                        # 如果仍然失败，尝试使用系统PATH中的驱动
                        self.driver = webdriver.Edge(options=options)
                        driver_initialized = True
                        print("成功使用系统PATH中的Edge驱动")
                else:
                    self.driver = webdriver.Edge(options=options)
                    driver_initialized = True
                    print("成功使用系统PATH中的Edge驱动")
            except Exception as e:
                print(f"备用方法初始化Edge驱动失败: {str(e)}")
        
        # 如果所有方式都失败，抛出异常
        if not driver_initialized:
            # 提供详细的错误解决建议
            error_msg = (
                "无法初始化Edge驱动，请确保：\n"
                "1. 已安装Microsoft Edge浏览器\n"
                "2. 安装对应版本的Edge WebDriver\n"
                "3. 或者安装webdriver-manager: pip install webdriver-manager\n"
                "4. 检查是否将Edge WebDriver添加到系统PATH中"
            )
            raise Exception(error_msg)
        
        # 执行脚本来隐藏自动化特征（如果可能）
        try:
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except:
            # 如果无法执行此脚本（某些新版浏览器不允许），则跳过
            pass

    def navigate_to(self, url):
        """
        导航到指定 URL
        
        :param url: 目标网址
        """
        try:
            self.driver.get(url)
            print(f"成功访问: {url}")
            return True
        except Exception as e:
            print(f"访问 {url} 失败: {str(e)}")
            return False

    def find_element(self, by, value, timeout=10):
        """
        查找单个元素
        
        :param by: 查找方式 (By.ID, By.CLASS_NAME, By.XPATH 等)
        :param value: 查找值
        :param timeout: 超时时间（秒）
        :return: 元素对象
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except Exception as e:
            print(f"查找元素失败: {str(e)}")
            return None

    def find_elements(self, by, value, timeout=0):
        """
        查找多个元素
        
        :param by: 查找方式
        :param value: 查找值
        :param timeout: 超时时间（秒）
        :return: 元素列表
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            elements = wait.until(EC.presence_of_all_elements_located((by, value)))
            return elements
        except Exception as e:
            print(f"查找元素失败: {str(e)}")
            return []

    def scrape_page_title(self):
        """
        获取页面标题
        """
        return self.driver.title

    def take_screenshot(self, filename="screenshot.png"):
        """
        截取屏幕截图
        
        :param filename: 文件名
        """
        try:
            self.driver.save_screenshot(filename)
            print(f"截图已保存: {filename}")
            return True
        except Exception as e:
            print(f"截图失败: {str(e)}")
            return False

    def get_page_source(self):
        """
        获取页面源码
        
        :return: 页面HTML源码
        """
        try:
            return self.driver.page_source
        except Exception as e:
            print(f"获取页面源码失败: {str(e)}")
            return ""

    def get_current_url(self):
        """
        获取当前页面URL
        
        :return: 当前页面URL
        """
        try:
            return self.driver.current_url
        except Exception as e:
            print(f"获取当前URL失败: {str(e)}")
            return ""

    def wait_and_click(self, by, value, timeout=10):
        """
        等待元素可点击并点击
        
        :param by: 查找方式
        :param value: 查找值
        :param timeout: 超时时间
        :return: 是否点击成功
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable((by, value)))
            element.click()
            return True
        except Exception as e:
            print(f"点击元素失败: {str(e)}")
            return False

    def wait_for_user_interaction(self, message="请完成页面上的交互，然后点击确定继续..."):
        """
        等待用户交互，使用PySide6弹窗
        
        :param message: 提示消息
        :return: 用户确认后继续
        """
        # 创建消息框
        msg_box = QMessageBox()
        msg_box.setWindowTitle("用户交互")
        msg_box.setText(message)
        msg_box.setInformativeText("请在浏览器中完成所需操作，完成后点击确定继续...")
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Ok)

        # 设置窗口标志，使弹窗始终显示在最前面
        msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)

        # 显示消息框并等待用户响应
        result = msg_box.exec_()

        if result == QMessageBox.Ok:
            print("用户点击确定，继续执行...")
            return True
        else:
            print("用户点击取消，停止执行")
            return False

    def close(self):
        """
        关闭浏览器
        """
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")


def example_usage():
    """
    使用示例
    """
    # 创建爬虫实例
    scraper = EdgeScraper(headless=False)  # 设为 True 可以无头模式运行
    
    try:
        # 访问网页
        success = scraper.navigate_to("https://www.baidu.com")
        if not success:
            print("无法访问目标网站")
            return

        # 截图
        scraper.take_screenshot("baidu_homepage.png")

        # 查找搜索框并输入内容
        search_box = scraper.find_element(By.ID, "kw")
        if search_box:
            search_box.clear()
            search_box.send_keys("Python Selenium")
            time.sleep(1)

            # 点击搜索按钮
            search_btn = scraper.find_element(By.ID, "su")
            if search_btn:
                search_btn.click()
                time.sleep(3)

                # 获取搜索结果标题
                titles = scraper.find_elements(By.CSS_SELECTOR, "h3")
                print(f"找到 {len(titles)} 个搜索结果:")
                
                for i, title in enumerate(titles[:5]):  # 显示前5个结果
                    print(f"{i+1}. {title.text}")

        # 获取页面标题
        title = scraper.scrape_page_title()
        print(f"\n页面标题: {title}")

        # 获取当前URL
        current_url = scraper.get_current_url()
        print(f"当前URL: {current_url}")

        # 截图搜索结果页
        scraper.take_screenshot("search_results.png")

        # 获取页面源码示例（仅前200字符）
        page_source = scraper.get_page_source()
        print(f"页面源码长度: {len(page_source)} 字符")
        print(f"页面源码预览: {page_source[:200]}...")

    except Exception as e:
        print(f"爬虫执行出错: {str(e)}")
    
    finally:
        # 关闭浏览器
        scraper.close()


if __name__ == "__main__":
    example_usage()