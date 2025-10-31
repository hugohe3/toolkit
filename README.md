# Python 工具集 (Python Toolkit)

一个实用的 Python 工具集合，包含坐标转换、PDF 处理、字幕转换等常用功能。

## 📋 目录

- [功能特性](#功能特性)
- [安装](#安装)
- [工具说明](#工具说明)
  - [1. 中国坐标系转换工具](#1-中国坐标系转换工具)
  - [2. PDF 书签拆分工具](#2-pdf-书签拆分工具)
  - [3. PDF 章节拆分工具](#3-pdf-章节拆分工具)
  - [4. SRT 字幕转 Markdown](#4-srt-字幕转-markdown)
  - [5. VTT 字幕转 Markdown](#5-vtt-字幕转-markdown)
  - [6. Markdown 文件合并工具](#6-markdown-文件合并工具)
- [环境要求](#环境要求)
- [作者](#作者)

## 功能特性

本工具集包含以下六个独立工具：

1. **坐标系转换** - 支持 WGS84、GCJ02（火星坐标）、BD09（百度坐标）之间的相互转换
2. **PDF 书签拆分** - 根据 PDF 文件的书签（大纲）自动拆分文档
3. **PDF 章节拆分** - 根据 PDF 文件的章节层级结构智能拆分文档
4. **SRT 转 Markdown** - 将 SRT 格式字幕批量转换为 Markdown 文档
5. **VTT 转 Markdown** - 将 VTT 格式字幕批量转换为 Markdown 文档
6. **Markdown 文件合并** - 将多个 Markdown 文件合并为一个文档

## 安装

### 环境要求

- Python 3.6+
- 依赖包：
  - PyPDF2（用于 PDF 处理工具）

### 安装依赖

```bash
pip install PyPDF2
```

### 下载使用

克隆或下载本仓库到本地：

```bash
git clone https://github.com/yourusername/toolkit.git
cd toolkit
```

## 工具说明

### 1. 中国坐标系转换工具

**文件：** `coordinate_converter.py`

**功能：** 提供中国常用坐标系之间的相互转换，包括 WGS84（GPS 标准坐标）、GCJ02（火星坐标系，高德/谷歌中国使用）、BD09（百度坐标系）。

#### 支持的坐标系

- **WGS84**: 国际标准坐标系（GPS 坐标）
- **GCJ02**: 火星坐标系（国测局坐标，高德、谷歌中国使用）
- **BD09**: 百度坐标系（百度地图使用）

#### 使用方法

**方式一：使用类方法（推荐）**

```python
from coordinate_converter import CoordinateConverter

# WGS84 转 GCJ02
gcj02_lon, gcj02_lat = CoordinateConverter.wgs84_to_gcj02(120.0, 30.0)

# GCJ02 转 WGS84
wgs84_lon, wgs84_lat = CoordinateConverter.gcj02_to_wgs84(120.0, 30.0)

# GCJ02 转 BD09
bd09_lon, bd09_lat = CoordinateConverter.gcj02_to_bd09(120.0, 30.0)

# BD09 转 GCJ02
gcj02_lon, gcj02_lat = CoordinateConverter.bd09_to_gcj02(120.0, 30.0)

# WGS84 转 BD09
bd09_lon, bd09_lat = CoordinateConverter.wgs84_to_bd09(120.0, 30.0)

# BD09 转 WGS84
wgs84_lon, wgs84_lat = CoordinateConverter.bd09_to_wgs84(120.0, 30.0)
```

**方式二：使用函数式接口（向后兼容）**

```python
from coordinate_converter import wgs84_to_gcj02, gcj02_to_wgs84

# WGS84 转 GCJ02
gcj02_lon, gcj02_lat = wgs84_to_gcj02(120.0, 30.0)

# GCJ02 转 WGS84
wgs84_lon, wgs84_lat = gcj02_to_wgs84(120.0, 30.0)
```

**直接运行测试：**

```bash
python coordinate_converter.py
```

#### 特性

- 自动判断坐标是否在中国境内
- 高精度转换算法
- 支持链式转换

---

### 2. PDF 书签拆分工具

**文件：** `split_pdf_by_bookmarks.py`

**功能：** 根据 PDF 文件的书签（大纲）自动拆分文档为多个独立的 PDF 文件，每个文件对应一个一级书签。

#### 使用方法

**命令行交互式运行：**

```bash
python split_pdf_by_bookmarks.py
```

运行后，程序会提示：
1. 输入 PDF 文件的完整路径
2. 输入输出文件名的前缀（可选，直接回车则不添加前缀）

**编程方式调用：**

```python
from split_pdf_by_bookmarks import split_pdf

# 拆分 PDF 文件
split_pdf("path/to/your/file.pdf", prefix="chapter")
```

#### 输出说明

- 输出目录：在输入文件所在目录创建 `<PDF文件名>_split` 文件夹
- 输出文件名格式：`[前缀_]序号-书签名.pdf`
- 保留每个拆分文件中的嵌套书签结构

#### 特性

- 自动识别并处理 PDF 书签
- 保留嵌套书签结构
- 自动处理文件名中的非法字符
- 支持自定义文件名前缀

---

### 3. PDF 章节拆分工具

**文件：** `split_pdf_by_chapters.py`

**功能：** 根据 PDF 文件的章节层级结构智能拆分文档，支持按章（一级书签）或按节（二级书签）两种拆分级别。

#### 使用方法

**命令行交互式运行：**

```bash
python split_pdf_by_chapters.py
```

运行后，程序会提示：
1. 输入 PDF 文件的完整路径
2. 选择拆分级别（1: 按章拆分，2: 按节拆分）

**编程方式调用：**

```python
from split_pdf_by_chapters import split_pdf

# 按章拆分
split_pdf("path/to/your/file.pdf", split_level=1)

# 按节拆分
split_pdf("path/to/your/file.pdf", split_level=2)
```

#### 输出说明

- 输出目录：在输入文件所在目录创建 `<PDF文件名>_chapters` 文件夹
- 按章拆分时，文件名格式：`序号-章名.pdf`
- 按节拆分时，文件名格式：`章序号-节序号-节名.pdf`

#### 特性

- 智能识别章节层级结构
- 支持中英文书签识别（章、节、Chapter、Section 等）
- 支持数字格式书签（如 "1. xxx"、"1.1 xxx"）
- 自动计算章节页码范围

---

### 4. SRT 字幕转 Markdown

**文件：** `srt_to_md.py`

**功能：** 批量将 SRT 格式字幕文件转换为 Markdown 文档，支持按章节组织的目录结构。

#### 使用方法

**命令行交互式运行：**

```bash
python srt_to_md.py
```

运行后，程序会提示输入要处理的文件夹路径。

**编程方式调用：**

```python
from srt_to_md import main

# 处理指定目录
main("path/to/your/directory")
```

#### 目录结构要求

```
根目录/
├── 章节1/
│   ├── 01-视频1.srt
│   ├── 02-视频2.srt
│   └── ...
├── 章节2/
│   ├── 01-视频1.srt
│   └── ...
└── ...
```

#### 输出说明

- 为每个章节文件夹生成一个对应的 Markdown 文件
- 文件名为 `章节名.md`
- 自动移除时间轴和序号，只保留纯文本内容
- 支持自然排序（chapter2 在 chapter10 之前）

#### 特性

- 自动去除时间轴和序号
- 智能合并多行字幕
- 按自然顺序排序文件
- 支持批量处理

---

### 5. VTT 字幕转 Markdown

**文件：** `vvt_to_md.py`

**功能：** 批量将 VTT 格式字幕文件转换为 Markdown 文档，支持按章节组织的目录结构。

#### 使用方法

**命令行交互式运行：**

```bash
python vvt_to_md.py
```

运行后，程序会提示输入要处理的文件夹路径。

**编程方式调用：**

```python
from vvt_to_md import main

# 处理指定目录
main("path/to/your/directory")
```

#### 目录结构要求

```
根目录/
├── 章节1/
│   ├── 01-视频1.vtt
│   ├── 02-视频2.vtt
│   └── ...
├── 章节2/
│   ├── 01-视频1.vtt
│   └── ...
└── ...
```

#### 输出说明

- 为每个章节文件夹生成一个对应的 Markdown 文件
- 文件名为 `章节名.md`
- 自动移除 WEBVTT 头部、时间轴等元数据
- 支持自然排序（chapter2 在 chapter10 之前）

#### 特性

- 自动处理 WEBVTT 格式头部
- 自动去除时间轴和元数据
- 智能合并多行字幕
- 按自然顺序排序文件
- 支持批量处理

---

### 6. Markdown 文件合并工具

**文件：** `merge_md.py`

**功能：** 将一个文件夹下的多个 Markdown 文件按顺序合并为一个 Markdown 文档，支持自定义输出格式和递归处理子目录。

#### 使用方法

**命令行交互式运行：**

```bash
python merge_md.py
```

运行后，程序会提示：
1. 输入包含 Markdown 文件的文件夹路径
2. 输入输出文件名（默认为 `merged.md`）
3. 是否递归处理子目录（默认为否）
4. 是否为每个文件添加标题（默认为是）
5. 是否在文件之间添加分隔符（默认为是）

**编程方式调用：**

```python
from merge_md import merge_markdown_files

# 基本合并
merge_markdown_files("path/to/markdown/folder")

# 自定义输出
merge_markdown_files(
    input_dir="path/to/markdown/folder",
    output_file="combined.md",
    add_separator=True,
    add_filename_header=True,
    recursive=False
)
```

#### 参数说明

- `input_dir` - 输入目录路径（必需）
- `output_file` - 输出文件名，默认为 `merged.md`
- `add_separator` - 是否在文件之间添加分隔符（`---`），默认为 `True`
- `add_filename_header` - 是否添加文件名作为二级标题，默认为 `True`
- `recursive` - 是否递归处理子目录，默认为 `False`

#### 输出说明

- 输出文件保存在输入目录下
- 文件按自然顺序排序（如 file1, file2, file10）
- 自动跳过输出文件本身（避免循环合并）
- 可选择添加文件名标题和分隔符

#### 特性

- 支持自然排序（符合人类习惯）
- 支持递归处理子目录
- 可自定义输出格式（标题、分隔符）
- 自动处理 UTF-8 编码
- 智能跳过空文件
- 避免循环合并（自动排除输出文件）

#### 使用场景

- 合并多个章节的 Markdown 笔记
- 整合分散的文档片段
- 批量处理学习资料
- 生成单一的文档用于导出或分享

---

## 环境要求

- **Python**: 3.6 或更高版本
- **操作系统**: Windows、macOS、Linux
- **依赖包**:
  - `PyPDF2` - PDF 处理工具所需

## 注意事项

1. **坐标转换工具**：仅对中国境内的坐标进行偏移处理，境外坐标不进行转换
2. **PDF 拆分工具**：需要 PDF 文件包含有效的书签结构
3. **字幕转换工具**：需要按章节组织目录结构，每个子文件夹视为一个章节

## 许可证

本项目采用 MIT 许可证。

## 作者

hugohe3

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**最后更新时间：** 2025年10月31日

