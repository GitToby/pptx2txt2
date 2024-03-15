from __future__ import annotations

import os
import re
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, DefaultDict, IO
from xml.etree.ElementTree import XML


def extract_text_per_slide(
    pptx_path: IO[Any] | os.PathLike[Any] | str,
) -> dict[int, str]:
    """Read a Word document into a string. Doesn't preserve whitespace.

    Parameters
    ----------
    pptx_path : IO[Any] | os.PathLike[Any]
        The path to the Powerpoint .pptx file from which the text is to be extracted.

    Returns
    -------
    text : dict[int, str]
        The text from each slide, including notes) the PowerPoint indexed by slide number (starting at 1)
    """
    text_content: DefaultDict[int, list[str]] = defaultdict(list)

    with zipfile.ZipFile(pptx_path, mode="r") as zip_:
        namelist = zip_.namelist()

        # the namelist is unordered
        # this sorted search provides an order for us to read in the data
        # "notedSlides" come after "slides" etc.
        for file_name in sorted(namelist, reverse=True):
            # make sure we ge the correct slide
            # patterns of relevant files:
            # - .../slide<N>.xml
            # - .../notesSlide<N>.xml
            # - .../ content.xml (this case the slide_idx is '' mapping to 0)
            search_res = re.search(
                r".*(?P<type>slide|notesSlide|content)(?P<index>[0-9]*).xml$", file_name
            )
            if search_res:
                slide_idx = search_res["index"]
                slide_idx_ = int(slide_idx) if slide_idx else 0

                # iterate string parts and join
                part_data = zip_.read(file_name)
                # question, remove <#> for slide numbers?
                part_text = " ".join(XML(part_data).itertext())
                text_content[slide_idx_].append(part_text)

    result = dict()
    # now we join each of the parts of the slides to one text block per slide
    # reverse the slides because the initial sort was reversed
    for idx, content in reversed(text_content.items()):
        # This removes multichar whitespace with 1 whitespace
        content_ = " ".join(" ".join(content).split())

        # proper format punctuation chars
        for char in (".", ",", "?"):
            content_ = content_.replace(f" {char}", char)

        result[idx] = content_

    return result


def extract_text(pptx_path: IO[Any] | os.PathLike[Any] | str) -> str:
    per_slide = extract_text_per_slide(pptx_path)
    return " ".join(per_slide.values())


def extract_images(
    pptx_path: IO[Any] | os.PathLike[Any] | str, img_dir: os.PathLike[Any] | str
):
    """Extract all images from the Word document and save in the directory `img_dir`

    Parameters
    ----------
    pptx_path : IO[Any] | os.PathLike[Any]
        The path to the Word document .pptx file from which the images are to be extracted.

    img_dir : os.PathLike[Any]
        The path to a directory where the images extracted from the Word document will be written to.

    Returns
    -------
    extracted_paths : list[Path]
        A list of image paths that were extracted from the document.

    Raises
    ------
    OSError
        If the `img_dir` is not a dir or doesn't exist.
    """
    img_dir_path = Path(img_dir)
    if not img_dir_path.is_dir():
        raise OSError(f"{img_dir} is not a directory.")

    extracted_paths: list[Path] = []

    with zipfile.ZipFile(pptx_path, mode="r") as zip_:
        filtered_files = (
            _file
            for _file in zip_.filelist
            if _file.filename.endswith(
                (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".avif", ".svg")
            )
        )

        for file in filtered_files:
            # We only want the filename added to our outdir
            out_file_name = Path(file.filename)
            out_path = img_dir_path / out_file_name.parts[-1]

            # Reading the file needs to be done in the zip.
            file_data = zip_.read(file.filename)
            with open(out_path, "wb") as f:
                f.write(file_data)
            extracted_paths.append(out_path)

    return extracted_paths
