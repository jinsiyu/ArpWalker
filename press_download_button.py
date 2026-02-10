import time

from selenium.webdriver.common.by import By


def press_download_button(scraper):
    download_button_list = scraper.find_elements(By.XPATH,
                                                 '''//i[@class="ci-download m-r text-xlg text-primary sslab-mr-xs"]''')
    print(f"找到 {len(download_button_list)} 个下载按钮:")
    for i, download_button in enumerate(download_button_list):
        scraper.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_button)
        # 执行JavaScript代码获取每个下载按钮对应的Angular对象数据
        # 使用execute_script执行JavaScript代码
        obj_data = scraper.driver.execute_script("""
                var element = arguments[0];
                var scope = angular.element(element).scope();
                return scope.obj ? JSON.stringify(scope.obj, null, 2) : 'No obj found';
            """, download_button)

        print(f"第{i + 1}个下载按钮的obj数据:")
        print(obj_data)
        print("-" * 50)

        # 获取并输出item数据
        item_data = scraper.driver.execute_script("""
                var element = arguments[0];
                var scope = angular.element(element).scope();
                return scope.item ? JSON.stringify(scope.item, null, 2) : 'No item found';
            """, download_button)

        print(f"第{i + 1}个下载按钮的item数据:")
        print(item_data)
        print("-" * 50)
        # 解析Angular对象数据
        try:
            obj_data = eval(obj_data) if obj_data != 'No obj found' else {}
            item_data_dict = eval(item_data) if item_data != 'No item found' else {}
            if 'APPENDIX_URL' in obj_data and 'APPENDIX_NAME' in obj_data:
                appendix_name = obj_data['APPENDIX_NAME']
                # 如果appendix_name以PJ-开头，则跳过下载
                if appendix_name.startswith('PJ-'):
                    print(f"跳过下载，因为APPENDIX_NAME以PJ-开头: {appendix_name}")
                else:
                    time.sleep(3)
                    # 检查是否存在MONEY_AMOUNT、SELLER_NAME、INVOICE_NUMBER字段
                    if 'MONEY_AMOUNT' in obj_data and 'SELLER_NAME' in obj_data and 'INVOICE_NUMBER' in obj_data:
                        # 构造新的文件名
                        new_appendix_name = f"发票_{obj_data['MONEY_AMOUNT']}元_{obj_data['SELLER_NAME']}_{obj_data['INVOICE_NUMBER']}_{obj_data['APPENDIX_NAME']}"
                    elif 'APPENDIX_TYPE' in obj_data and obj_data['APPENDIX_TYPE'] == 'BXSXFC0028':
                        # 对于APPENDIX_TYPE为BXSXFC0028的文件，构造新的文件名
                        new_appendix_name = f"外包审批单_{obj_data['APPENDIX_NAME']}"
                    elif 'APPENDIX_TYPE' in obj_data and obj_data['APPENDIX_TYPE'] == 'BXSXFC0029':
                        # 对于APPENDIX_TYPE为BXSXFC0029的文件，构造新的文件名
                        new_appendix_name = f"合同_{obj_data['APPENDIX_NAME']}"
                    elif 'APPENDIX_TYPE' in obj_data and obj_data['APPENDIX_TYPE'] == 'BXSXFC0030':
                        # 对于APPENDIX_TYPE为BXSXFC0030的文件，构造新的文件名
                        new_appendix_name = f"验收单（尾款）_{obj_data['APPENDIX_NAME']}"
                    elif 'APPENDIX_TYPE' in obj_data and obj_data['APPENDIX_TYPE'] == 'payRecord':
                        # 对于APPENDIX_TYPE为payRecord的文件，构造新的文件名
                        new_appendix_name = f"支付记录附件和情况说明_{obj_data['APPENDIX_NAME']}"
                    elif 'APPENDIX_TYPE' in obj_data and obj_data['APPENDIX_TYPE'] == 'payImg':
                        # 对于APPENDIX_TYPE为payImg的文件，构造新的文件名
                        new_appendix_name = f"购物截图附件和情况说明_{obj_data['APPENDIX_NAME']}"
                    elif 'RECEIPT_CODE' in item_data_dict and 'SERIAL_NUMBER' in item_data_dict and 'AMT' in item_data_dict:
                        # 检查item数据中是否存在RECEIPT_CODE、SERIAL_NUMBER和AMT字段，构造新的文件名
                        new_appendix_name = f"银行回单_{item_data_dict['RECEIPT_CODE']}_{item_data_dict['SERIAL_NUMBER']}_{item_data_dict['AMT']}"
                    else:
                        # 不符合要求的附件文件名改为附件_APPENDIX_NAME
                        new_appendix_name = f"附件_{obj_data['APPENDIX_NAME']}"
                    
                    # 构造JavaScript调用downLoad函数
                    js_code = f"""
                        var element = arguments[0];
                        var scope = angular.element(element).scope();
                        if (scope && typeof scope.downLoad === 'function') {{
                            scope.downLoad(new MouseEvent('click'), '{obj_data['APPENDIX_URL']}', '{new_appendix_name}');
                        }} else {{
                            console.log('downLoad function not found in scope');
                        }}
                    """
                    # 执行JavaScript代码调用downLoad函数
                    scraper.driver.execute_script(js_code, download_button)
                    print(f"已执行downLoad函数，URL: {obj_data['APPENDIX_URL']}, NAME: {new_appendix_name}")
            else:
                print("缺少必要的APPENDIX_URL或APPENDIX_NAME字段")
        except Exception as e:
            print(f"解析Angular对象数据时出错: {e}")

        #download_button.click()
        print(f"已点击第{i + 1}个下载按钮元素")