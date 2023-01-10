from requests import get as req_get
from yattag import Doc, indent
from utils import Lang, SvgPos
from PIL import ImageFont


GITHUB_COLORS = {
    name: data["color"]
    for name, data in req_get("https://raw.githubusercontent.com/ozh/github-colors/master/colors.json").json().items()
}

SVG_WIDTH, SVG_HEIGHT = 1000, 30
BAR_POS = SvgPos(0, 0, 1000, 8)
ACCURACY = 3  # How many digits to use after the decimal point

NAME_COLOR = "rgb(139, 148, 158)"
GITHUB_BACKGROUND_COLOR = "rgb(13, 17, 23)"

FONT_SIZE = 12
FONT_SIZEREF_FILE = "src/segoeui.ttf"
NAME_WIDTH_THRESHOLD = 0.7
NAME_Y_OFFSET = 14
OTHER_LANGS_NAME = "Other"


def get_text_size(text, font_size, font_name):
    return ImageFont.truetype(font_name, font_size).getbbox(text)[2:]


def generate_bar(languages: list[Lang], total_bytes: int):
    languages = sorted(languages, key=lambda item: -item.bbytes)

    doc, tag, text = Doc().tagtext()
    with tag(
        "svg",
        xmlns="http://www.w3.org/2000/svg",
        viewBox=f"0 0 {SVG_WIDTH} {SVG_HEIGHT}",
        width=SVG_WIDTH, height=SVG_HEIGHT,
        # style=f"background-color:{GITHUB_BACKGROUND_COLOR}"
    ):
        with tag("style"), open("src/svg_styles.css", encoding="utf-8") as file:
            text(file.read().strip())

        with tag("mask", id="bar_border_radius"):
            doc.stag(
                "rect",
                # x=0, y=0,
                # maskUnits="objectBoundingBox",
                width=BAR_POS.width, height=BAR_POS.height,
                fill="#fff",
                rx=round(min(BAR_POS.width, BAR_POS.height) / 2, ACCURACY)
            )

        text_pos = []  # (x_center, width)

        with tag("g", mask="url(#bar_border_radius)", transform=f"translate({BAR_POS.x},{BAR_POS.y})"):
            prev_bytes = 0
            for lang in languages:
                color = GITHUB_COLORS.get(lang.name)
                if color is None:
                    print(f'Warning! Could not find color for language "{lang.name}"')

                # Calculate positioning
                x_offset = BAR_POS.width * prev_bytes / total_bytes
                prev_bytes += lang.bbytes
                x_end = BAR_POS.width * prev_bytes / total_bytes
                x_center = (x_offset + x_end) / 2

                x_offset = round(x_offset, ACCURACY)
                x_center = round(x_center, ACCURACY)
                x_end = round(x_end, ACCURACY)  # should be equal to x_offset on next iteration

                width = round(x_end - x_offset, ACCURACY)
                text_pos.append((x_center, width))

                # Draw bar piece
                doc.stag("rect", klass="bar_piece", x=x_offset, width=width, height=BAR_POS.height, fill=(color or ""))

            show_other_bar = prev_bytes < total_bytes
            if show_other_bar:
                x_offset = BAR_POS.width * prev_bytes / total_bytes
                x_center = (x_offset + BAR_POS.width) / 2
                x_offset = round(x_offset, ACCURACY)
                x_center = round(x_center, ACCURACY)

                width = round(BAR_POS.width - x_offset, ACCURACY)
                text_pos.append((x_center, width))
                doc.stag(
                    "rect", klass="bar_piece", x=x_offset, width=width, height=BAR_POS.height, fill="url(#stripes)"
                )

        with tag(
            "g", transform=f"translate({BAR_POS.x},{round(BAR_POS.y + BAR_POS.height + NAME_Y_OFFSET, ACCURACY)})"
        ):
            for i, lang in enumerate(languages):
                text_size = get_text_size(lang.name, FONT_SIZE, FONT_SIZEREF_FILE)
                if text_size[0] <= text_pos[i][1] * NAME_WIDTH_THRESHOLD:
                    x = round(text_pos[i][0] - text_size[0] / 2, ACCURACY)
                    with tag("text", x=x, fill=NAME_COLOR):
                        text(lang.name)

            if show_other_bar:
                text_size = get_text_size(OTHER_LANGS_NAME, FONT_SIZE, FONT_SIZEREF_FILE)
                if text_size[0] <= text_pos[-1][1] * NAME_WIDTH_THRESHOLD:
                    x = round(text_pos[-1][0] - text_size[0] / 2, ACCURACY)
                    with tag("text", x=x, fill=NAME_COLOR):
                        text(OTHER_LANGS_NAME)

        if show_other_bar:
            with tag("defs"):
                strip_size = 5
                strip_color = NAME_COLOR
                with tag("pattern", id="stripes", width=strip_size, height=strip_size, patternUnits="userSpaceOnUse"):
                    doc.stag(
                        "polygon",
                        points=f"{strip_size * 0.75},0 {strip_size},0 {strip_size},{strip_size * 0.25}",
                        fill=strip_color
                    )
                    doc.stag(
                        "polygon",
                        points=f"0,0 {strip_size},{strip_size} {strip_size * 0.75},{strip_size} 0,{strip_size * 0.25}",
                        fill=strip_color
                    )

    return doc.getvalue()


def beautify(svg: str) -> str:
    return indent(svg)


if __name__ == "__main__":  # Development & manual testing
    import os
    os.chdir("../")

    import json
    with open("output/github_colors_dump.test.json", 'w', encoding="utf-8") as file:
        json.dump(GITHUB_COLORS, file, ensure_ascii=False, indent=4)

    languages = [
        Lang(tag='python', name='Python', bbytes=141512),
        Lang(tag='c++', name='C++', bbytes=7860)
    ]
    # total_bytes = 300000
    total_bytes = sum(lang.bbytes for lang in languages)

    print(bar := beautify(generate_bar(languages, total_bytes)))
    with open("output/bar.test.svg", 'w', encoding="utf-8") as file:
        file.write(bar)

    # print(get_text_size("Python", 12, "segoeui.ttf"))
