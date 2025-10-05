"""PDF书签拆分工具模块。

此模块提供根据 PDF 文件的书签（大纲）自动拆分文档的功能。
可以保留每个拆分文件中的嵌套书签结构，并支持自定义文件名前缀。
"""

import os
from PyPDF2 import PdfReader, PdfWriter
from typing import List, Dict, Tuple


def get_bookmarks_with_pages(pdf_reader: PdfReader) -> List[Tuple[str, int, int]]:
    """获取PDF文件的书签及其对应的页面范围。

    解析 PDF 文件的书签结构，计算每个书签对应的页码范围。书签按页码顺序排序，每个书签的结束页码为下一个书签的起始页码减1。

    :param pdf_reader: PDF阅读器对象
    :return: 书签信息列表 [(书签名, 起始页码, 结束页码), ...]

    .. note::
       页码从0开始计数，最后一个书签的结束页码为PDF的最后一页，跳过无效书签
    """
    outlines = pdf_reader.outline
    bookmarks = []

    if not outlines:
        return []

    # 首先收集所有有效书签及其页码
    valid_bookmarks = []
    for i in range(len(outlines)):
        try:
            # 跳过非页面书签
            if not isinstance(outlines[i], dict) or '/Page' not in str(outlines[i]):
                continue

            current_title = outlines[i].title if hasattr(
                outlines[i], 'title') else f"Chapter {i+1}"
            try:
                current_page = pdf_reader.get_destination_page_number(
                    outlines[i])
                valid_bookmarks.append((current_title, current_page))
            except:
                print(f"警告: 跳过无效书签: {current_title}")
                continue
        except Exception as e:
            print(f"警告: 处理书签时出错: {str(e)}")
            continue

    # 按页码排序书签
    valid_bookmarks.sort(key=lambda x: x[1])

    # 计算每个书签的页码范围
    for i, (title, start_page) in enumerate(valid_bookmarks):
        # 如果不是最后一个书签，结束页码是下一个书签的起始页码减1
        if i < len(valid_bookmarks) - 1:
            end_page = valid_bookmarks[i+1][1] - 1
        else:
            # 最后一个书签的结束页码是PDF的最后一页
            end_page = len(pdf_reader.pages) - 1

        bookmarks.append((title, start_page, end_page))
    return bookmarks


def get_nested_bookmarks(pdf_reader: PdfReader, start_page: int, end_page: int) -> List[Dict]:
    """获取指定页面范围内的所有书签。

    从 PDF 文件中提取指定页码范围内的书签，包括嵌套的子书签。书签的页码会被重新计算为相对于新PDF的页码（从0开始）。

    :param pdf_reader: PDF阅读器对象
    :param start_page: 起始页码（包含）
    :param end_page: 结束页码（包含）
    :return: 书签列表，每个元素包含 title、page 和 children

    .. note::
       返回的书签页码是相对于拆分后PDF的页码，而不是原PDF的页码
    """
    def process_outline(outline, parent_list=None, page_offset=0):
        if parent_list is None:
            parent_list = []

        if isinstance(outline, list):
            for item in outline:
                process_outline(item, parent_list, page_offset)
        elif isinstance(outline, dict) and '/Page' in str(outline):
            try:
                page_num = pdf_reader.get_destination_page_number(outline)
                if start_page <= page_num <= end_page:
                    # 计算在新PDF中的页码（相对于片段的起始页）
                    new_page_num = page_num - start_page
                    title = outline.title if hasattr(
                        outline, 'title') else "Untitled Bookmark"
                    parent_list.append({
                        'title': title,
                        'page': new_page_num,
                        'children': []
                    })
            except:
                pass

    result = []
    process_outline(pdf_reader.outline, result)
    return result


def create_valid_filename(title: str) -> str:
    """创建有效的文件名。

    移除文件名中的非法字符，确保生成的文件名在不同操作系统中都有效。

    :param title: 原始标题字符串
    :return: 处理后的合法文件名

    .. note::
       会移除以下非法字符: < > : " / \\ | ? *
    """
    # 替换Windows文件系统中的非法字符
    invalid_chars = '<>:"/\\|?*'
    filename = ''.join(c if c not in invalid_chars else '_' for c in title)
    return filename.strip()


def add_bookmarks_to_pdf(pdf_writer: PdfWriter, bookmarks: List[Dict], parent=None) -> None:
    """将书签添加到PDF文件。

    递归地将书签结构添加到 PDF 文件中，保留原有的层级关系。

    :param pdf_writer: PDF写入器对象
    :param bookmarks: 书签列表，每个元素包含 title、page 和 children
    :param parent: 父书签对象，用于创建嵌套结构

    .. note::
       此函数会递归处理嵌套的子书签
    """
    for bookmark in bookmarks:
        current = pdf_writer.add_outline_item(
            bookmark['title'],
            bookmark['page'],
            parent
        )
        if bookmark['children']:
            add_bookmarks_to_pdf(pdf_writer, bookmark['children'], current)


def split_pdf(pdf_path: str, prefix: str = "") -> None:
    """根据书签拆分PDF文件。

    根据 PDF 文件的一级书签将文档拆分为多个独立的 PDF 文件。每个拆分文件保留原有的书签结构，文件名基于书签标题生成。

    :param pdf_path: PDF文件的完整路径
    :param prefix: 输出文件名的前缀，默认为空

    .. note::
       - 输出目录为 "<PDF文件名>_split"，创建在输入文件所在目录
       - 输出文件名格式: "[前缀_]序号-书签名.pdf"
       - 如果书签名包含非法字符，会自动替换为下划线
    """
    try:
        # 获取输入PDF文件所在的目录和文件名
        input_dir = os.path.dirname(pdf_path)
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

        # 在输入文件所在目录创建输出目录
        output_dir = os.path.join(input_dir, f"{pdf_name}_split")
        os.makedirs(output_dir, exist_ok=True)

        # 打开PDF文件
        print(f"正在处理PDF文件: {pdf_path}")
        pdf_reader = PdfReader(pdf_path)

        # 获取书签信息
        bookmarks = get_bookmarks_with_pages(pdf_reader)
        if not bookmarks:
            print("未找到有效书签，无法拆分PDF文件")
            return

        print(f"找到 {len(bookmarks)} 个有效书签")

        # 根据书签拆分PDF
        for i, (title, start_page, end_page) in enumerate(bookmarks, 1):
            try:
                pdf_writer = PdfWriter()

                # 添加页面到新的PDF
                for page_num in range(start_page, end_page + 1):
                    if page_num < len(pdf_reader.pages):
                        pdf_writer.add_page(pdf_reader.pages[page_num])

                # 获取并添加该范围内的书签
                nested_bookmarks = get_nested_bookmarks(
                    pdf_reader, start_page, end_page)
                add_bookmarks_to_pdf(pdf_writer, nested_bookmarks)

                # 添加主书签
                if not nested_bookmarks:
                    # 如果没有嵌套书签，至少添加一个主书签
                    pdf_writer.add_outline_item(title, 0)

                # 创建输出文件名
                safe_title = create_valid_filename(title)
                # 添加用户指定的前缀到文件名
                if prefix:
                    output_filename = f"{prefix}_{i:02d}-{safe_title}.pdf"
                else:
                    output_filename = f"{i:02d}-{safe_title}.pdf"
                output_path = os.path.join(output_dir, output_filename)

                # 保存拆分后的PDF
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)

                print(
                    f"已创建: {output_filename} (页码范围: {start_page}-{end_page})")

            except Exception as e:
                print(f"警告: 处理章节 '{title}' 时出错: {str(e)}")
                continue

        print(f"\n拆分完成！文件保存在: {output_dir}")

    except Exception as e:
        print(f"处理PDF时出错: {str(e)}")


def main() -> None:
    """主函数。

    程序入口点，通过命令行交互获取 PDF 文件路径和输出前缀，然后执行拆分操作。
    """
    # 获取用户输入的PDF文件路径
    pdf_path = input("请输入PDF文件的完整路径: ").strip()

    # 同时处理单引号和双引号
    if (pdf_path.startswith('"') and pdf_path.endswith('"')) or \
       (pdf_path.startswith("'") and pdf_path.endswith("'")):
        pdf_path = pdf_path[1:-1]
    if not os.path.exists(pdf_path):
        print("错误：文件不存在！")
        print(f"当前路径: {os.getcwd()}")
        print(f"尝试访问: {pdf_path}")
        return

    if not pdf_path.lower().endswith('.pdf'):
        print("错误：请提供PDF文件！")
        return
    # 获取用户输入的前缀
    prefix = input("请输入输出文件名的前缀(直接回车则不添加前缀): ").strip()
    split_pdf(pdf_path, prefix)


if __name__ == "__main__":
    main()
