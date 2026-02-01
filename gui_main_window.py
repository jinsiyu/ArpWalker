import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QMessageBox, \
    QHBoxLayout, QLineEdit
from PySide6.QtCore import Qt

from ciomp_scraper import demonstrate_ciomp_login_process
# 导入各种处理器模块
from expense_handler import handle_expense_page
from expense_list_handler import handle_expense_list_page

from consumable_purchase_order_handler import handle_consumable_purchase_order_page
from consumable_purchase_order_list_handler import handle_consumable_purchase_order_list_page

from consumable_stock_handler import handle_consumable_stock_page
from consumable_stock_list_handler import handle_consumable_stock_list_page

from fix_asset_purchase_order_handler import handle_fix_asset_purchase_order_page
from fix_asset_purchase_order_list_handler import handle_fix_asset_purchase_order_list_page

from fix_asset_stock_handler import handle_fix_asset_stock_page
from fix_asset_stock_list_handler import handle_fix_asset_stock_list_page

from edge_scraper import EdgeScraper


class MainWindow(QWidget):
    def __init__(self, scraper):
        super().__init__()
        self.scraper = scraper
        self.setWindowTitle("ARP系统数据抓取工具")
        self.setGeometry(300, 300, 600, 400)
        
        # 设置主布局
        layout = QVBoxLayout()
        
        # 添加标题标签
        title_label = QLabel("请选择操作类型")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title_label)
        
        # 添加超时时间设置区域
        timeout_layout = QHBoxLayout()
        timeout_label = QLabel("超时时间(秒):")
        timeout_label.setStyleSheet("font-size: 14px;")
        
        self.timeout_input = QLineEdit()
        self.timeout_input.setPlaceholderText("请输入超时时间")
        self.timeout_input.setText("5")  # 默认值为5
        self.timeout_input.setMaximumWidth(100)
        
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self.timeout_input)
        timeout_layout.addStretch()  # 添加弹性空间
        
        layout.addLayout(timeout_layout)
        
        # 创建按钮网格
        button_grid = QGridLayout()
        
        # 定义按钮配置
        buttons_config = [
            ("报销单", "expense"),
            ("耗材采购单", "consumable_purchase"),
            ("耗材验收单", "consumable_stock"),
            ("资产采购单", "fix_asset_purchase"),
            ("资产验收单", "fix_asset_stock")
        ]
        
        # 创建按钮并添加到网格中
        for row, (label, prefix) in enumerate(buttons_config):
            # 单页面抓取按钮
            single_button = QPushButton(f"{label}单页面抓取")
            single_button.setObjectName(f"{prefix}_single")
            single_button.clicked.connect(lambda _, p=prefix: self.handle_single_page(p))
            
            # 列表抓取按钮
            list_button = QPushButton(f"{label}列表抓取")
            list_button.setObjectName(f"{prefix}_list")
            list_button.clicked.connect(lambda _, p=prefix: self.handle_list_page(p))
            
            # 将按钮添加到网格中
            button_grid.addWidget(single_button, row, 0)
            button_grid.addWidget(list_button, row, 1)
        
        # 设置按钮最小尺寸和样式
        for i in range(button_grid.rowCount()):
            for j in range(button_grid.columnCount()):
                item = button_grid.itemAtPosition(i, j)
                if item and item.widget():
                    button = item.widget()
                    button.setMinimumSize(200, 50)
                    button.setStyleSheet(
                        "QPushButton {"
                        "   font-size: 14px;"
                        "   padding: 10px;"
                        "   margin: 5px;"
                        "}"
                        "QPushButton:hover {"
                        "   background-color: #f0f0f0;"
                        "}"
                        "QPushButton:pressed {"
                        "   background-color: #d0d0d0;"
                        "}"
                    )
        
        layout.addLayout(button_grid)
        
        # 添加退出按钮
        exit_button = QPushButton("退出")
        exit_button.clicked.connect(self.close)
        exit_button.setStyleSheet(
            "QPushButton {"
            "   font-size: 14px;"
            "   padding: 8px;"
            "   background-color: #ff6b6b;"
            "   color: white;"
            "   border: none;"
            "   border-radius: 4px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #ff5252;"
            "}"
            "QPushButton:pressed {"
            "   background-color: #e53e3e;"
            "}"
        )
        layout.addWidget(exit_button)
        
        self.setLayout(layout)

    def handle_single_page(self, prefix):
        """处理单页面抓取操作"""
        handlers_map = {
            'expense': handle_expense_page,
            'consumable_purchase': handle_consumable_purchase_order_page,
            'consumable_stock': handle_consumable_stock_page,
            'fix_asset_purchase': handle_fix_asset_purchase_order_page,
            'fix_asset_stock': handle_fix_asset_stock_page
        }
        
        if prefix in handlers_map:
            handler_func = handlers_map[prefix]
            self.execute_handler_function(handler_func, is_list=False)
        else:
            QMessageBox.warning(self, "警告", f"未找到对应的处理器: {prefix}")

    def handle_list_page(self, prefix):
        """处理列表抓取操作"""
        handlers_map = {
            'expense': handle_expense_list_page,
            'consumable_purchase': handle_consumable_purchase_order_list_page,
            'consumable_stock': handle_consumable_stock_list_page,
            'fix_asset_purchase': handle_fix_asset_purchase_order_list_page,
            'fix_asset_stock': handle_fix_asset_stock_list_page
        }
        
        if prefix in handlers_map:
            handler_func = handlers_map[prefix]
            self.execute_handler_function(handler_func, is_list=True)
        else:
            QMessageBox.warning(self, "警告", f"未找到对应的处理器: {prefix}")

    def execute_handler_function(self, handler_func, is_list, timeout=5):
        """执行处理器函数"""
        try:
            # 隐藏界面
            self.hide()
            # 执行处理函数，传递scraper和timeout参数
            handler_func(self.scraper, timeout=timeout)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"执行处理器时发生错误: {str(e)}")
        finally:
            # 任务完成后重新显示界面
            self.show()


if __name__ == "__main__":
    """
    主函数
    """
    print("长春光机所数字平台爬虫 - 登录后页面爬取")
    print("=" * 60)

    # 启动GUI应用
    scraper = EdgeScraper(headless=False)
    app = QApplication(sys.argv)
    demonstrate_ciomp_login_process(scraper)
    window = MainWindow(scraper)
    window.show()


    # 在应用退出时关闭浏览器
    def close_scraper():
        try:
            scraper.close()
        except:
            print("浏览器可能已关闭")


    app.aboutToQuit.connect(close_scraper)
    sys.exit(app.exec())