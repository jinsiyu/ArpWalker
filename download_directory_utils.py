import os
import shutil

from path import Path


def change_download_dir(download_dir: Path, scraper):
    download_path = str(download_dir.absolute())
    scraper.driver.command_executor._commands["send_command"] = ("POST",
                                                                 '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior',
              'params': {'behavior': 'allow', 'downloadPath': download_path}}
    command_result = scraper.driver.execute("send_command", params)


def create_download_dir(download_dir: Path):
    if download_dir.exists():
        print(f"下载目录已存在: {download_dir.absolute()}")
        shutil.rmtree(download_dir.absolute())
    else:
        print(f"下载目录不存在: {download_dir.absolute()}")

    os.mkdir(download_dir.absolute())
    print(f"创建下载目录: {download_dir.absolute()}")