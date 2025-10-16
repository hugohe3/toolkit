# Toolkit 实用脚本合集

本仓库收集了一些常用的本地实用脚本，覆盖坐标转换、PDF 拆分、字幕转 Markdown 等场景。

## 内容概览

- `coordinate_converter.py` — 中国常用坐标系转换（WGS84 / GCJ02 / BD09）
- `split_pdf_by_bookmarks.py` — 按 PDF 书签拆分，保留嵌套书签
- `split_pdf_by_chapters.py` — 按章节/小节拆分 PDF（一级/二级书签）
- `srt_to_md.py` — 批量将 SRT 字幕合并为 Markdown
- `vvt_to_md.py` — 批量将 VTT 字幕合并为 Markdown

## 环境要求

- Python 3.8+
- 依赖：`PyPDF2`（仅 PDF 相关脚本需要）

安装依赖：

```bash
pip install -U PyPDF2
# 或 macOS 上：
pip3 install -U PyPDF2
```

建议使用虚拟环境（可选）：

```bash
python -m venv .venv && source .venv/bin/activate  # Windows 使用 .venv\\Scripts\\activate
pip install -U PyPDF2
```

## 使用方法

### 1) 按书签拆分 PDF

命令：

```bash
python split_pdf_by_bookmarks.py
```

交互式输入：

- PDF 文件完整路径（支持带空格的路径，必要时加引号）
- 输出文件名前缀（可选）

输出：

- 在源文件所在目录创建目录：`<PDF文件名>_split`
- 文件名格式：`[前缀_]序号-书签名.pdf`
- 会保留范围内的嵌套书签（如存在）

### 2) 按章/节拆分 PDF

命令：

```bash
python split_pdf_by_chapters.py
```

交互式输入：

- PDF 文件完整路径
- 拆分级别：`1`（按章，一级书签）或 `2`（按节，二级书签）

输出：

- 在源文件所在目录创建目录：`<PDF文件名>_chapters`
- 按章：`序号-章名.pdf`
- 按节：`章序号-节序号-节名.pdf`

### 3) 坐标系转换（WGS84 / GCJ02 / BD09）

作为模块导入使用（推荐）：

```python
from coordinate_converter import CoordinateConverter

gcj_lon, gcj_lat = CoordinateConverter.wgs84_to_gcj02(120.0, 30.0)
wgs_lon, wgs_lat = CoordinateConverter.gcj02_to_wgs84(120.0, 30.0)
bd_lon, bd_lat = CoordinateConverter.gcj02_to_bd09(120.0, 30.0)
```

也可直接运行查看示例输出：

```bash
python coordinate_converter.py
```

### 4) SRT → Markdown（按章节目录批量合并）

目录结构示例：

```
/path/to/root
├─ Chapter1/
│  ├─ 001.srt
│  └─ 002.srt
└─ Chapter2/
   └─ 001.srt
```

命令：

```bash
python srt_to_md.py
```

交互式输入根目录路径，程序会在根目录生成对应的 `ChapterX.md` 文件。

### 5) VTT → Markdown（按章节目录批量合并）

使用方式与 SRT 相同：

```bash
python vvt_to_md.py
```

交互式输入根目录路径，程序会在根目录生成对应的 `ChapterX.md` 文件。

## 小贴士

- 路径中包含空格时，命令行输入可用引号包裹：`"/path/with space/file.pdf"`
- 生成的 Markdown 文件编码为 UTF-8。
- 若遇到 PDF 无有效书签，相关拆分脚本会给出提示并退出。

