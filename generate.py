from typing import List, Tuple
import click
from PIL import Image, ImageFile, ImageEnhance
from click.exceptions import BadParameter
import os
import itertools
import glob


@click.command()
@click.option(
    "--input",
    "-i",
    help="Input image.",
    required=True,
    type=click.File("rb"),
)
@click.option(
    "--output",
    "-o",
    help="Directory to output the files.",
    required=True,
    type=click.Path(file_okay=False),
)
@click.option(
    "--width", "-w", help="Width of each rectangle in pixels.", required=True, type=int
)
def main(input, output: str, width: int):
    """Gerenerate spotlight sprites. Image should be composed of rectangles that can be on or off."""
    if not os.path.exists(output):
        os.makedirs(output)
    for f in glob.glob(os.path.join(output, "*.png")):
        os.remove(f)

    with Image.open(input) as im:
        total_width = im.width
        if total_width % width != 0:
            raise BadParameter(
                f"total width of image is {total_width}, must be dividable by {width}"
            )

        num_recs = int(total_width / width)

        off_base = greyscale(im)
        on_recs = [crop_rec(im, i, width) for i in range(num_recs)]

        total_sprites = int(2**num_recs)
        print(
            f"Generating {total_sprites} sprites for {num_recs} rectangle combinations"
        )

        stuff = list(range(0, num_recs))
        for L in range(len(stuff) + 1):
            for subset in itertools.combinations(stuff, L):
                if len(subset):
                    generate(off_base, on_recs, width, subset, output)


def crop_rec(im: ImageFile, i: int, width: int):
    region = ((i * width), 0, ((i + 1) * width), im.height)
    return im.copy().crop(region)


def greyscale(im: ImageFile):
    grey = im.copy().convert("L").convert("RGB")
    darken = ImageEnhance.Brightness(grey).enhance(0.25)
    return darken

def generate(
    off_base: Image,
    recs: List,
    rec_width: int,
    selected: Tuple[int],
    output_dir: str,
):
    output = os.path.join(output_dir, "_".join(map(str, selected)) + ".png")

    img = off_base.copy()
    for i in selected:
        region = ((i * rec_width), 0, ((i + 1) * rec_width), img.height)
        img.paste(recs[i], region)

    img.save(output)
    print(output)

if __name__ == "__main__":
    main()
