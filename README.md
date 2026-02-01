# ARP系统数据抓取工具

基于Selenium控制Microsoft Edge浏览器的自动化工具，专门用于长春光机所数字平台（ARP系统）的数据抓取和处理。

## 功能特性

- 控制Microsoft Edge浏览器进行网页自动化操作
- 支持有头模式和无头模式运行
- 提供丰富的页面交互功能（点击、输入、滚动等）
- 元素定位和内容提取
- 页面截图功能
- JavaScript执行支持
- GUI图形界面，方便用户操作
- 支持多种ARP系统单据处理：
  - 报销单（单页面和列表）
  - 耗材采购单（单页面和列表）
  - 耗材验收单（单页面和列表）
  - 资产采购单（单页面和列表）
  - 资产验收单（单页面和列表）
- 自动提取单据编号并创建相应文件夹
- 自动下载相关文件并按单号重命名
- 支持自定义超时时间

## 安装依赖

在运行项目之前，请先安装所需依赖：

```bash
pip install -r requirements.txt
```

## 快速开始

### 运行GUI界面

```bash
python gui_main_window.py
```

### 基本使用流程

1. 运行GUI程序
2. 在浏览器中完成登录操作
3. 选择要处理的单据类型（报销单、耗材采购单、耗材验收单、资产采购单、资产验收单）
4. 选择单页面抓取或列表抓取
5. 系统会自动提取单据信息并下载相关文件

## 项目结构

- `edge_scraper.py`: Edge浏览器自动化核心类
- `gui_main_window.py`: GUI图形用户界面
- `ciomp_scraper.py`: 长春光机所登录流程处理
- `form_handler.py`: 表单页面处理
- `download_directory_utils.py`: 下载目录管理工具
- `modify_appendix_name.py`: 附件名称修改工具
- `expense_handler.py` / `expense_list_handler.py`: 报销单处理
- `consumable_purchase_order_handler.py` / `consumable_purchase_order_list_handler.py`: 耗材采购单处理
- `consumable_stock_handler.py` / `consumable_stock_list_handler.py`: 耗材验收单处理
- `fix_asset_purchase_order_handler.py` / `fix_asset_purchase_order_list_handler.py`: 固定资产采购单处理
- `fix_asset_stock_handler.py` / `fix_asset_stock_list_handler.py`: 固定资产验收单处理

## 使用说明

1. 运行 `python gui_main_window.py` 启动GUI界面
2. 在浏览器中完成ARP系统的登录操作
3. 在GUI界面中选择相应的单据类型和处理模式
4. 系统会自动提取单据信息，并将相关文件下载到以单据号命名的文件夹中
5. 支持自定义超时时间，可根据网络状况调整

## 注意事项

1. 确保系统已安装Microsoft Edge浏览器
2. 遵守网站的使用条款和相关政策
3. 合理使用自动化工具，避免对服务器造成过大压力
4. 对于动态内容较多的页面，可能需要增加等待时间
5. 如果无法联网下载驱动，确保本地已安装匹配版本的EdgeDriver

## 离线环境配置

如果在离线环境中使用，需要预先安装EdgeDriver：

1. 下载与你的Edge浏览器版本匹配的EdgeDriver：https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
2. 将其路径添加到系统PATH环境变量，或
3. 在代码中指定驱动路径：`driver = webdriver.Edge(executable_path='/path/to/msedgedriver')`