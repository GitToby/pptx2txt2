from __future__ import annotations

import os
import zipfile
from collections import defaultdict
from itertools import chain
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
        namelist = sorted(zip_.namelist())
        # These files are for both pptx
        slides_files = (f for f in namelist if "slides" in f and f.endswith(".xml"))
        notes_files = (f for f in namelist if "notesSlides" in f and f.endswith(".xml"))
        slides_and_notes = zip(slides_files, notes_files)

        # these files are for odp formats
        odp_files = ([f] for f in namelist if f == "content.xml")

        # iterate over each sublist [[slide1, slide1_notes], [slide2, ...], ...]
        for i, slide in enumerate(chain(slides_and_notes, odp_files)):
            # iterate over each part of the sublist [slide1, slide1_notes]
            slide_content = text_content[i + 1]
            for part in slide:
                part_data = zip_.read(part)
                part_text = list(XML(part_data).itertext())
                # question, remove <#> for slide numbers?
                slide_content.append(" ".join(part_text))

    result = dict()
    for idx, content in text_content.items():
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
