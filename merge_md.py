"""Markdown文件合并工具模块。

此模块提供了将一个文件夹下的多个Markdown文件合并为单个Markdown文档的功能。
支持自然排序、自动添加分隔符、保留原文件标题结构等特性。
"""

import os
import re
from pathlib import Path
from typing import List


def natural_sort_key(s: str) -> list:
    """自然排序的键函数。

    将字符串中的数字部分转换为整数进行比较，实现符合人类习惯的排序。
    例如：'file2.md' 会排在 'file10.md' 之前。

    :param s: 待排序的字符串
    :return: 包含整数和字符串的混合列表，用作排序键
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', str(s))]


def read_md_file(file_path: Path) -> str:
    """读取单个Markdown文件的内容。

    :param file_path: Markdown文件的路径
    :return: 文件的文本内容

    .. note::
       使用 UTF-8 编码读取文件，确保中文等字符正常显示
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"警告: 读取文件 {file_path.name} 时出错: {str(e)}")
        return ""


def merge_markdown_files(
    input_dir: str,
    output_file: str = "merged.md",
    add_separator: bool = True,
    add_filename_header: bool = True,
    recursive: bool = False
) -> None:
    """合并指定目录下的所有Markdown文件。

    将目录下的所有 .md 文件按自然排序合并为一个文件。可以选择是否添加分隔符和文件名标题。

    :param input_dir: 输入目录路径
    :param output_file: 输出文件名，默认为 "merged.md"
    :param add_separator: 是否在文件之间添加分隔符，默认为 True
    :param add_filename_header: 是否添加文件名作为二级标题，默认为 True
    :param recursive: 是否递归处理子目录，默认为 False

    .. note::
       - 输出文件保存在输入目录下
       - 文件按自然顺序排序（如 file1, file2, file10）
       - 自动跳过输出文件本身（避免循环合并）
    """
    input_path = Path(input_dir)

    if not input_path.exists() or not input_path.is_dir():
        print(f"错误: 路径 '{input_dir}' 不存在或不是一个文件夹")
        return

    # 获取所有Markdown文件
    if recursive:
        md_files = list(input_path.rglob('*.md'))
    else:
        md_files = list(input_path.glob('*.md'))

    # 按自然顺序排序
    md_files.sort(key=lambda x: natural_sort_key(str(x)))

    # 过滤掉输出文件本身（如果存在）
    output_path = input_path / output_file
    md_files = [f for f in md_files if f.resolve() != output_path.resolve()]

    if not md_files:
        print(f"在目录 '{input_dir}' 中没有找到Markdown文件")
        return

    print(f"找到 {len(md_files)} 个Markdown文件")
    print("=" * 60)

    # 合并文件内容
    merged_content = []

    for i, md_file in enumerate(md_files, 1):
        file_name = md_file.stem  # 不带扩展名的文件名
        relative_path = md_file.relative_to(input_path)
        
        print(f"[{i}/{len(md_files)}] 正在处理: {relative_path}")

        # 读取文件内容
        content = read_md_file(md_file)

        if not content.strip():
            print(f"    警告: 文件为空，跳过")
            continue

        # 添加文件名作为标题（如果启用）
        if add_filename_header:
            # 如果是递归模式，使用相对路径作为标题
            if recursive:
                header = f"## {relative_path}\n\n"
            else:
                header = f"## {file_name}\n\n"
            merged_content.append(header)

        # 添加文件内容
        merged_content.append(content.strip())

        # 添加分隔符（如果启用且不是最后一个文件）
        if add_separator and i < len(md_files):
            merged_content.append("\n\n---\n\n")
        else:
            merged_content.append("\n\n")

    # 写入合并后的文件
    try:
        with open(output_path, 'w', encoding='utf-8') as output:
            output.write('\n'.join(merged_content))
        print("=" * 60)
        print(f"✓ 合并完成！")
        print(f"输出文件: {output_path}")
        print(f"合并了 {len(md_files)} 个文件")
    except Exception as e:
        print(f"错误: 写入输出文件时出错: {str(e)}")


def main() -> None:
    """主函数。

    程序入口点，通过命令行交互获取用户输入，配置合并选项并执行合并操作。
    """
    print("=" * 60)
    print("Markdown 文件合并工具")
    print("=" * 60)
    print()

    # 获取输入目录
    input_dir = input("请输入包含Markdown文件的文件夹路径: ").strip()

    # 去除可能的引号
    input_dir = input_dir.strip('"\'')

    # 检查路径是否存在
    if not os.path.isdir(input_dir):
        print(f"错误: 路径 '{input_dir}' 不存在或不是一个文件夹")
        return

    # 获取输出文件名
    output_file = input("请输入输出文件名 (默认: merged.md): ").strip()
    if not output_file:
        output_file = "merged.md"
    elif not output_file.endswith('.md'):
        output_file += '.md'

    # 询问是否递归处理子目录
    recursive_choice = input("是否递归处理子目录? (y/n, 默认: n): ").strip().lower()
    recursive = recursive_choice in ('y', 'yes', '是')

    # 询问是否添加文件名标题
    header_choice = input("是否为每个文件添加标题? (y/n, 默认: y): ").strip().lower()
    add_filename_header = header_choice not in ('n', 'no', '否')

    # 询问是否添加分隔符
    separator_choice = input("是否在文件之间添加分隔符? (y/n, 默认: y): ").strip().lower()
    add_separator = separator_choice not in ('n', 'no', '否')

    print()
    print("开始合并...")
    print()

    # 执行合并
    merge_markdown_files(
        input_dir=input_dir,
        output_file=output_file,
        add_separator=add_separator,
        add_filename_header=add_filename_header,
        recursive=recursive
    )


if __name__ == "__main__":
    main()

