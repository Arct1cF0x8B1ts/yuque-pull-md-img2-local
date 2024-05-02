import os
import re
import requests
from urllib.parse import urlparse
import urllib3
urllib3.disable_warnings()


def get_image_links_from_md(md_file):
    # 读取Markdown文档内容
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 使用正则表达式提取图片链接
    image_links = re.findall(r'!\[.*?\]\((.*?)\)', content)

    return image_links, content

def download_images(image_links, folder_name):
    # 下载并保存图片到指定文件夹
    downloaded_image_paths = {}
    for link in image_links:
        image_name = os.path.basename(urlparse(link).path)
        image_path = os.path.join(folder_name, image_name)
        try:
            with requests.get(link, stream=True, verify=False) as r:
                r.raise_for_status()
                with open(image_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"Downloaded {image_name}")
            downloaded_image_paths[link] = image_path
        except Exception as e:
            print(f"Failed to download {image_name}: {e}")
    return downloaded_image_paths

def update_md_with_relative_paths(md_file, content, downloaded_image_paths):
    # 更新Markdown文档中的图片链接为下载后图片的相对路径
    for original_link, new_path in downloaded_image_paths.items():
        relative_path = os.path.relpath(new_path, os.path.dirname(md_file))
        content = content.replace(original_link, relative_path)
    # 写回Markdown文件
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Markdown file updated with relative image paths.")

if __name__ == "__main__":
    # Markdown文档所在文件夹路径
    folder_path = "/"
    
    # 对目录进行深度递归 返回为list
    md_files = [os.path.join(dirpath, filename) for dirpath, dirnames, filenames in os.walk(folder_path) for filename in filenames]
    for md_file in md_files:
        # 获取Markdown文档名称
        md_name = os.path.splitext(os.path.basename(md_file))[0]

        # 获取图片链接和Markdown文档内容
        image_links, md_content = get_image_links_from_md(md_file)

        # 创建保存图片的文件夹，以Markdown文档命名文件夹
        image_folder = os.path.join(os.path.dirname(md_file), md_name)
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

        # 下载图片并获取下载后的图片路径
        downloaded_image_paths = download_images(image_links, image_folder)

        # 更新Markdown文档中的图片链接为下载后图片的相对路径
        update_md_with_relative_paths(md_file, md_content, downloaded_image_paths)
