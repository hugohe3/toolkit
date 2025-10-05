"""SRT字幕文件转Markdown工具模块。

此模块提供了将SRT格式字幕文件转换为Markdown格式的功能。
支持批量处理多个章节目录下的SRT文件，并为每个章节生成对应的Markdown文档。
"""

import os
import re
from pathlib import Path


def process_srt_file(srt_path: Path) -> str:
    """处理单个SRT文件，去掉时间轴和换行。

    从SRT字幕文件中提取纯文本内容，移除序号、时间轴等元数据，并将多行字幕合并为单行文本。

    :param srt_path: SRT文件的路径
    :return: 处理后的纯文本内容

    .. note::
       SRT文件格式包含：序号 -> 时间轴 -> 字幕文本 -> 空行 -> 重复
    """
    with open(srt_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 移除时间轴和序号
    # SRT格式通常是: 序号 -> 时间轴 -> 文本内容 -> 空行 -> 重复
    lines = content.split('\n')
    processed_text = []
    i = 0

    while i < len(lines):
        # 跳过序号行
        if lines[i].strip().isdigit():
            i += 1
            # 跳过时间轴行 (通常格式为 00:00:00,000 --> 00:00:00,000)
            if i < len(lines) and '-->' in lines[i]:
                i += 1
                # 收集文本内容直到遇到空行
                text_chunk = []
                while i < len(lines) and lines[i].strip():
                    text_chunk.append(lines[i].strip())
                    i += 1
                # 将文本块合并为一行
                if text_chunk:
                    processed_text.append(' '.join(text_chunk))
        else:
            i += 1

    return ' '.join(processed_text)


def natural_sort_key(s: str) -> list:
    """自然排序的键函数。

    将字符串中的数字部分转换为整数进行比较，实现符合人类习惯的排序。例如：'chapter2' 会排在 'chapter10' 之前。

    :param s: 待排序的字符串
    :return: 包含整数和字符串的混合列表，用作排序键
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', str(s))]


def main(root_dir: str) -> None:
    """处理根目录下所有章节文件夹中的SRT文件。

    遍历指定根目录下的所有子文件夹，将每个文件夹中的SRT文件合并转换为一个Markdown文件。章节和文件按自然顺序排序。

    :param root_dir: 包含章节文件夹的根目录路径

    .. note::
       每个子文件夹被视为一个章节，生成的Markdown文件以章节名命名，文件夹和SRT文件按自然顺序排序
    """
    root_path = Path(root_dir)

    # 获取所有章节文件夹并按自然顺序排序
    chapter_dirs = [d for d in root_path.iterdir() if d.is_dir()]
    chapter_dirs.sort(key=natural_sort_key)

    for chapter_dir in chapter_dirs:
        chapter_name = chapter_dir.name
        print(f"处理章节: {chapter_name}")

        # 创建对应的markdown文件
        markdown_content = f"# {chapter_name}\n\n"

        # 获取章节目录下所有的SRT文件并按自然顺序排序
        srt_files = list(chapter_dir.glob('*.srt'))
        srt_files.sort(key=natural_sort_key)

        if not srt_files:
            print(f"  章节 {chapter_name} 中没有找到SRT文件")
            continue

        for srt_file in srt_files:
            file_name = srt_file.stem  # 不带扩展名的文件名
            print(f"  处理文件: {file_name}")

            # 处理SRT文件
            processed_content = process_srt_file(srt_file)

            # 添加到markdown内容
            markdown_content += f"## {file_name}\n\n{processed_content}\n\n"

        # 写入markdown文件
        markdown_path = root_path / f"{chapter_name}.md"
        with open(markdown_path, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_content)

        print(f"  已生成Markdown文件: {markdown_path}")


if __name__ == "__main__":
    # 主程序入口：通过命令行交互获取目标文件夹路径，验证后执行转换操作
    target_directory: str = input("请输入要处理的文件夹路径: ")

    # 去除可能的引号（用户可能复制带引号的路径）
    target_directory = target_directory.strip('"\'')

    # 检查路径是否存在
    if not os.path.isdir(target_directory):
        print(f"错误: 路径 '{target_directory}' 不存在或不是一个文件夹")
    else:
        main(target_directory)
