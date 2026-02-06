import time

from path import Path


def modify_report_name(download_dir: Path, possible_pdf_names: list[str] | str, new_name: str):
    # 统一处理 possible_pdf_names 为列表
    if isinstance(possible_pdf_names, str):
        possible_pdf_names = [possible_pdf_names]

    old_pdf_path = None
    for pdf_name in possible_pdf_names:
        temp_path = download_dir / pdf_name
        if temp_path.exists():
            old_pdf_path = temp_path
            break

    new_pdf_path = download_dir / new_name

    # 等待文件下载完成（如果还未下载）
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
            print(
                f"已将{old_pdf_path} 重命名为 {final_new_path.name} (原名称 {new_pdf_path.name} 已存在，使用新名称)")
        else:
            print(f"已将 {old_pdf_path} 重命名为 {final_new_path.name}")
    else:
        print(f"警告: 未找到 {old_pdf_path} 文件，可能下载失败或名称不同")