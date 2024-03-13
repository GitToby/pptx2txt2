from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import pptx2txt2

RESOURCES_DIR = Path(__file__).parent / "resources"

test_paths = [RESOURCES_DIR / "example_1.pptx", RESOURCES_DIR / "example_1.odp"]


@pytest.fixture
def pptx_path():
    return test_paths[0]


@pytest.fixture
def odp_path():
    return test_paths[1]


def test_example_1_extract_text_per_slide(pptx_path):
    per_slide_content = pptx2txt2.extract_text_per_slide(pptx_path)

    assert isinstance(per_slide_content, dict)

    assert len(per_slide_content) == 6

    assert per_slide_content[1] == (
        "Title Page I'm a subtitle - this page has no slide number too.. "
        "speaker notes for page 1"
    )
    assert per_slide_content[2] == (
        "This is the second slide I'm a presentation doc with some content. "
        "I have bold bits, italic bits, and bits of both. "
        "There are maybe two or three fonts and even an extra colour or two. "
        "Some docs, like this one even have emojis ☺️. "
        "Remember that links are a thing too. "
        "And tables {D1A04390-931B-4358-B36D-7A23B6FE7D81} A Table as well with bold italic colour ⁉️ fonts ‹#›"
    )
    assert per_slide_content[3] == "There are slides with images ‹#›"
    assert per_slide_content[4] == (
        "And slides with shapes with text Shape Text 1! Shape Text 2! Shape Text 4! ‹#›"
        " speaker notes for page 4"
    )
    assert (
        per_slide_content[5]
        == "well i think theyre charts There are charts too they got shapes… ‹#›"
    )
    assert per_slide_content[6] == "‹#› Word art is so 00s"


def test_example_1_extract_text(pptx_path):
    per_slide_content = pptx2txt2.extract_text_per_slide(pptx_path)
    content = pptx2txt2.extract_text(pptx_path)
    assert isinstance(content, str)
    assert all(ps_content in content for ps_content in per_slide_content.values())


def test_example_odp_extract_text(pptx_path, odp_path):
    content_pptx = pptx2txt2.extract_text(pptx_path)
    content_odp = pptx2txt2.extract_text(odp_path)

    # odp extracts with a subset of the content
    content_pptx = content_pptx.replace("‹#›", "<number>")

    # odp dosent leave the placeholder for images
    content_pptx = content_pptx.replace("{D1A04390-931B-4358-B36D-7A23B6FE7D81}", "")

    # remove extra whitespace
    content_pptx = " ".join(content_pptx.split())

    assert content_odp == content_pptx


@pytest.mark.parametrize("path", test_paths, ids=str)
def test_example_1_extract_images(path):
    with TemporaryDirectory() as tempdir:
        images = pptx2txt2.extract_images(path, tempdir)

        if "odp" in str(path):
            # odp files create a thumbnail file too
            assert len(images) == 2
        else:
            assert len(images) == 1

        assert tempdir in str(images[0])


def test_example_1_extract_images_bad_dir(pptx_path):
    with pytest.raises(OSError):
        pptx2txt2.extract_images(pptx_path, "/non/existent/dir")


def test_benchmark_pptx2txt2(benchmark, pptx_path):
    res = benchmark(pptx2txt2.extract_text_per_slide, pptx_path)
    assert res
