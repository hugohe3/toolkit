"""PDF章节拆分工具模块。

此模块提供根据 PDF 文件的书签层级结构智能拆分文档的功能。
支持按章（一级书签）或按节（二级书签）两种拆分级别。
"""

import os
from PyPDF2 import PdfReader, PdfWriter
from typing import List, Dict, Any


def get_bookmark_level(bookmark: Any) -> int:
    """判断书签的级别。

    通过分析书签标题中的关键词和格式，判断书签属于哪个级别。支持中文和英文书签识别。

    :param bookmark: PDF书签对象
    :return: 书签级别，1=一级书签(章)，2=二级书签(节)，0=其他

    .. note::
       识别规则：一级书签包含"章"、"chapter"、"part"等；二级书签包含"节"、"section"等；数字格式如 "1. xxx" 为章，"1.1 xxx" 为节
    """
    if not isinstance(bookmark, dict) or '/Page' not in str(bookmark):
        return 0

    title = bookmark.title if hasattr(bookmark, 'title') else ""
    title_lower = title.lower()

    # 一级书签(章)标识
    chapter_indicators = [
        "章",  # 中文章节 (如 "第一章")
        "chapter",  # 英文章节
        "part"  # 部分
    ]

    # 二级书签(节)标识
    section_indicators = [
        "节",  # 中文节
        "section",  # 英文节
        "小节"
    ]
    if any(indicator in title_lower for indicator in chapter_indicators):
        return 1
    elif any(indicator in title_lower for indicator in section_indicators):
        return 2

    # 根据标题格式判断
    # 如果以数字开头且后面跟着点(如"1. xxx", "1.1 xxx")
    if title.strip() and title[0].isdigit():
        parts = title.split('.')
        if len(parts) == 2:  # 形如"1. xxx"
            return 1
        elif len(parts) >= 3:  # 形如"1.1 xxx"或"1.1.1 xxx"
            return 2

    return 0  # 其他情况


def get_bookmarks_hierarchy(pdf_reader: PdfReader) -> List[Dict[str, Any]]:
    """获取PDF文件的书签层次结构。

    解析 PDF 书签，构建包含章节和子节的层次结构。自动计算每个章节和子节的页码范围。

    :param pdf_reader: PDF阅读器对象
    :return: 章节信息列表，每个元素包含 title、start_page、end_page 和 sections

    .. note::
       返回的字典结构：title（章节标题）、start_page（起始页码）、end_page（结束页码）、sections（子节列表）
    """
    outlines = pdf_reader.outline
    if not outlines:
        return []

    # 找出所有书签及其级别
    bookmarks_info = []
    for i, bookmark in enumerate(outlines):
        level = get_bookmark_level(bookmark)
        if level > 0:  # 只处理识别出级别的书签
            try:
                page_num = pdf_reader.get_destination_page_number(bookmark)
                title = bookmark.title if hasattr(
                    bookmark, 'title') else f"Bookmark {i+1}"
                bookmarks_info.append({
                    'title': title,
                    'page': page_num,
                    'level': level,
                    'index': i
                })
            except Exception as e:
                print(f"警告: 处理书签 '{bookmark}' 时出错: {str(e)}")

    # 构建章节结构
    chapters = []
    current_chapter = None

    for i, bookmark in enumerate(bookmarks_info):
        if bookmark['level'] == 1:  # 一级书签(章)
            # 如果有上一个章节，计算其结束页码
            if current_chapter is not None:
                current_chapter['end_page'] = bookmark['page'] - 1
            # 创建新章节
            current_chapter = {
                'title': bookmark['title'],
                'start_page': bookmark['page'],
                'end_page': len(pdf_reader.pages) - 1,  # 默认到文档末尾，后面可能会更新
                'sections': []
            }
            chapters.append(current_chapter)

        elif bookmark['level'] == 2 and current_chapter is not None:  # 二级书签(节)
            # 添加到当前章节的子节点
            section = {
                'title': bookmark['title'],
                'start_page': bookmark['page'],
                'end_page': len(pdf_reader.pages) - 1  # 默认到文档末尾，后面可能会更新
            }

            # 更新上一个节的结束页码
            if current_chapter['sections']:
                current_chapter['sections'][-1]['end_page'] = bookmark['page'] - 1

            current_chapter['sections'].append(section)

    # 处理最后一个节的结束页码
    if chapters and chapters[-1]['sections']:
        last_section = chapters[-1]['sections'][-1]
        last_section['end_page'] = chapters[-1]['end_page']

    return chapters


def create_valid_filename(title: str) -> str:
    """创建有效的文件名。

    移除文件名中的非法字符，确保生成的文件名在不同操作系统中都有效。

    :param title: 原始标题字符串
    :return: 处理后的合法文件名

    .. note::
       会移除以下非法字符: < > : " / \\ | ? *
    """
    # 替换Windows和macOS文件系统中的非法字符
    invalid_chars = '<>:"/\\|?*'
    filename = ''.join(c if c not in invalid_chars else '_' for c in title)
    return filename.strip()


def split_pdf(pdf_path: str, split_level: int = 1) -> None:
    """根据书签层级拆分PDF文件。

    根据 PDF 文件的书签层级结构智能拆分文档。可以选择按章（一级书签）或按节（二级书签）进行拆分。

    :param pdf_path: PDF文件的完整路径
    :param split_level: 拆分级别，1=按章拆分，2=按节拆分，默认为1

    .. note::
       - 输出目录为 "<PDF文件名>_chapters"，创建在输入文件所在目录
       - 按章拆分时，文件名格式: "序号-章名.pdf"
       - 按节拆分时，文件名格式: "章序号-节序号-节名.pdf"
       - 如果某章没有子节，按节拆分时会保留整章
    """
    try:
        # 获取输入PDF文件所在的目录和文件名
        input_dir = os.path.dirname(pdf_path)
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

        # 在输入文件所在目录创建输出目录
        output_dir = os.path.join(input_dir, f"{pdf_name}_chapters")
        os.makedirs(output_dir, exist_ok=True)

        # 打开PDF文件
        print(f"正在处理PDF文件: {pdf_path}")
        pdf_reader = PdfReader(pdf_path)

        # 获取书签层次结构
        chapters = get_bookmarks_hierarchy(pdf_reader)

        if not chapters:
            print("未找到有效的书签结构，无法拆分PDF文件")
            return

        print(f"找到 {len(chapters)} 个章节")

        # 根据拆分级别处理
        if split_level == 1:  # 按章拆分
            for i, chapter in enumerate(chapters, 1):
                try:
                    pdf_writer = PdfWriter()

                    # 添加页面到新的PDF
                    for page_num in range(chapter['start_page'], chapter['end_page'] + 1):
                        if page_num < len(pdf_reader.pages):
                            pdf_writer.add_page(pdf_reader.pages[page_num])

                    # 创建输出文件名
                    safe_title = create_valid_filename(chapter['title'])
                    output_filename = f"{i:02d}-{safe_title}.pdf"
                    output_path = os.path.join(output_dir, output_filename)

                    # 保存拆分后的PDF
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)

                    print(f"已创建章节: {output_filename}")

                except Exception as e:
                    print(f"警告: 处理章节 '{chapter['title']}' 时出错: {str(e)}")
                    continue

        elif split_level == 2:  # 按节拆分
            section_count = 1
            for i, chapter in enumerate(chapters, 1):
                # 如果没有子节，则按章处理
                if not chapter['sections']:
                    try:
                        pdf_writer = PdfWriter()

                        # 添加页面到新的PDF
                        for page_num in range(chapter['start_page'], chapter['end_page'] + 1):
                            if page_num < len(pdf_reader.pages):
                                pdf_writer.add_page(pdf_reader.pages[page_num])

                        # 创建输出文件名
                        safe_title = create_valid_filename(chapter['title'])
                        output_filename = f"{i:02d}-{safe_title}.pdf"
                        output_path = os.path.join(output_dir, output_filename)

                        # 保存拆分后的PDF
                        with open(output_path, 'wb') as output_file:
                            pdf_writer.write(output_file)

                        print(f"已创建章节: {output_filename}")
                        section_count += 1
                    except Exception as e:
                        print(f"警告: 处理章节 '{chapter['title']}' 时出错: {str(e)}")
                        continue
                else:
                    # 处理每个子节
                    for j, section in enumerate(chapter['sections'], 1):
                        try:
                            pdf_writer = PdfWriter()

                            # 添加页面到新的PDF
                            for page_num in range(section['start_page'], section['end_page'] + 1):
                                if page_num < len(pdf_reader.pages):
                                    pdf_writer.add_page(
                                        pdf_reader.pages[page_num])

                            # 创建输出文件名 (章节号-小节号-标题)
                            safe_title = create_valid_filename(
                                section['title'])
                            output_filename = f"{i:02d}-{j:02d}-{safe_title}.pdf"
                            output_path = os.path.join(
                                output_dir, output_filename)

                            # 保存拆分后的PDF
                            with open(output_path, 'wb') as output_file:
                                pdf_writer.write(output_file)

                            print(f"已创建小节: {output_filename}")
                            section_count += 1

                        except Exception as e:
                            print(
                                f"警告: 处理小节 '{section['title']}' 时出错: {str(e)}")
                            continue
        print(f"\n拆分完成！文件保存在: {output_dir}")

    except Exception as e:
        print(f"处理PDF时出错: {str(e)}")


def main() -> None:
    """主函数。

    程序入口点，通过命令行交互获取 PDF 文件路径和拆分级别，然后执行拆分操作。
    """
    # 获取用户输入的PDF文件路径，并处理可能的引号问题
    pdf_path = input("请输入PDF文件的完整路径: ")

    # 去除路径中可能存在的引号（单引号和双引号）
    pdf_path = pdf_path.strip().strip("'").strip('"')

    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        print(f"错误：文件不存在！路径: {pdf_path}")
        return

    if not pdf_path.lower().endswith('.pdf'):
        print("错误：请提供PDF文件！")
        return

    # 询问拆分级别
    while True:
        split_choice = input("请选择拆分级别 (1: 按章拆分, 2: 按节拆分): ").strip()
        if split_choice in ('1', '2'):
            split_level = int(split_choice)
            break
        else:
            print("无效选择，请输入1或2")
    split_pdf(pdf_path, split_level)


if __name__ == "__main__":
    main()
