# pptx2txt2

[![codecov](https://codecov.io/gh/GitToby/pptx2txt2/graph/badge.svg?token=12KF8ARYVZ)](https://codecov.io/gh/GitToby/pptx2txt2)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/GitToby/pptx2txt2/lint-and-test.yaml)](https://github.com/GitToby/pptx2txt2/actions/workflows/lint-and-test.yaml)
[![GitHub file size in bytes](https://img.shields.io/github/size/GitToby/pptx2txt2/src%2Fpptx2txt2%2F__init__.py)](https://github.com/GitToby/pptx2txt2/blob/master/src/pptx2txt2/__init__.py)
[![PyPI - License](https://img.shields.io/pypi/l/pptx2txt2)](https://github.com/GitToby/pptx2txt2/blob/master/LICENSE.txt)
[![PyPI - Version](https://img.shields.io/pypi/v/pptx2txt2)](https://pypi.org/project/pptx2txt2/)
[![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FGitToby%2Fpptx2txt2%2Fmaster%2Fpyproject.toml)](https://pypi.org/project/pptx2txt2/)

My personal replacement for [pptx2txt](https://github.com/shakiyam/pptx2txt). 

It's intended to be very simple and provide some utilities to extract content similar to the original lib.

Also see
    - [docx2txt2](https://github.com/GitToby/docx2txt2) for docx conversion

## Usage

Install with your fave package manager (anything that pulls from pypi will work. pip, poetry, pdm, etx)

```
pip install pptx2txt2
```

Use with any [`PathLike`](https://docs.python.org/3/library/os.html#os.PathLike) object, like a filepath or IO stream.

There are 3 methods
- `extract_text_per_slide` returns a `dict[int, str]` of per slide content & notes
- `extract_text` utility to join all slide content
- `extract_images` copy images over to another dir

```python
import io
from pathlib import Path
import pptx2txt2

# path
text = pptx2txt2.extract_text("path/to/my.pptx")
text_per_slide = pptx2txt2.extract_text_per_slide("path/to/my.pptx")
image_paths = pptx2txt2.extract_images("path/to/my.pptx", "path/to/images/out")

# actual Paths
pptx_path = Path(__file__).parent / "my.pptx"
image_out = Path(__file__).parent / "my" / "images"
image_out.mkdir(parents=True)

text2 = pptx2txt2.extract_text(pptx_path)
text_per_slide2 = pptx2txt2.extract_text_per_slide(pptx_path)
image_paths2 = pptx2txt2.extract_images(pptx_path, image_out)

# bytestreams
pptx_bytes = b"..."
bytes_io = io.BytesIO(pptx_bytes)
text3 = pptx2txt2.extract_text(bytes_io)
text_per_slide3 = pptx2txt2.extract_text_per_slide(bytes_io)
image_paths3 = pptx2txt2.extract_images(bytes_io, "path/to/images/out")
```


# Considerations
- Doesn't preserve whitespace or styling like the original; new slides, tabs and the like are now just spaces.
- headers and footers contain "<#>" of "<number>" where there would be a number, unlike the original which removed them
- pptx files have a UUID in text where images were.

## Benchmarks

Basic benchmarking using [pytest-benchmark](https://pytest-benchmark.readthedocs.io) with a basic test document on my M1 macbook and on GithubActions.

Macbook:

```
------------------------------------------------ benchmark: 1 tests -----------------------------------------------
Name (time in ms)               Min     Max    Mean  StdDev  Median     IQR  Outliers       OPS  Rounds  Iterations
-------------------------------------------------------------------------------------------------------------------
test_benchmark_pptx2txt2     2.4750  8.5452  2.6080  0.5790  2.5176  0.0503      4;34  383.4367     273           1
-------------------------------------------------------------------------------------------------------------------
```

GitHub Actions, python 3.12:

```
```
