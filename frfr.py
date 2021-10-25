from PIL import Image, ImageChops
from itertools import chain, combinations, product
import enum


@enum.unique
class T(enum.Enum):
    """Image transformations"""

    FLIP_LEFT_RIGHT = 0  # PIL.Image.FLIP_LEFT_RIGHT
    FLIP_TOP_BOTTOM = 1  # PIL.Image.FLIP_TOP_BOTTOM
    ROTATE_LEFT = 2  # PIL.Image.ROTATE_90, rotate 90° counterclockwise
    ROTATE_180 = 3  # PIL.Image.ROTATE_180
    ROTATE_RIGHT = 4  # PIL.Image.ROTATE_270, rotate 90° clockwise


# Base image transformations, i.e. any sequence of image transformations can be
# rewritten in terms of the base image transformations. For example, (ROTATE_LEFT,) is
# (r,r,r)
f = T.FLIP_TOP_BOTTOM
r = T.ROTATE_RIGHT

# Equivalence classes for all possible base transformation sequences of the length of
# up to four. The first transformation sequence in a class is usually shorter than any
# other transformation sequence from the class and therefore it is chosen as a
# representative transformation sequence for the class. That is, any other
# transformation sequence from the class can be replaced by the representative
# transformation sequence.
R = ((r,), (f, f, r), (r, f, f))
F = ((f,), (f, f, f), (r, f, r))
RR = ((r, r), (r, r, f, f), (f, f, r, r), (f, r, r, f), (r, f, f, r))  # ROTATE_180
FF = ID = ((), (f, f), (r, r, r, r), (f, f, f, f), (r, f, r, f), (f, r, f, r))
RF = ((r, f), (r, r, f, r), (f, r, r, r), (r, f, f, f), (f, f, r, f))
FR = ((f, r), (r, r, r, f), (r, f, r, r), (f, r, f, f), (f, f, f, r))
RRR = ((r, r, r), (f, r, f))  # ROTATE_LEFT
FRR = ((f, r, r), (r, r, f))  # FLIP_LEFT_RIGHT

# A set of all equivalence classes
ALL_EQ = {R, F, RR, FF, RF, FR, RRR, FRR}

# Maps reduced sequences of base transformations to their equivalent rich counterparts
# and back.
BIJECTIVE_BASE_RICH_MAP = {
    (T.ROTATE_RIGHT,): (T.ROTATE_RIGHT,),
    (T.FLIP_TOP_BOTTOM,): (T.FLIP_TOP_BOTTOM,),
    (T.ROTATE_RIGHT, T.ROTATE_RIGHT): (T.ROTATE_180,),
    (T.ROTATE_180,): (T.ROTATE_RIGHT, T.ROTATE_RIGHT),
    (): (),
    (T.ROTATE_RIGHT, T.FLIP_TOP_BOTTOM): (T.ROTATE_RIGHT, T.FLIP_TOP_BOTTOM),
    (T.FLIP_TOP_BOTTOM, T.ROTATE_RIGHT): (T.FLIP_TOP_BOTTOM, T.ROTATE_RIGHT),
    (T.ROTATE_RIGHT, T.ROTATE_RIGHT, T.ROTATE_RIGHT): (T.ROTATE_LEFT,),
    (T.ROTATE_LEFT,): (T.ROTATE_RIGHT, T.ROTATE_RIGHT, T.ROTATE_RIGHT),
    (T.FLIP_TOP_BOTTOM, T.ROTATE_RIGHT, T.ROTATE_RIGHT): (T.FLIP_LEFT_RIGHT,),
    (T.FLIP_LEFT_RIGHT,): (T.FLIP_TOP_BOTTOM, T.ROTATE_RIGHT, T.ROTATE_RIGHT),
}


def reduce_base_form(transformation_sequence):
    """Reduce a sequence of base transformations."""

    def representative(transformation_sequence):
        """For the given transformation sequence return a representative sequence from the
        corresponding equivalence class."""
        for EQ in ALL_EQ:
            if transformation_sequence in EQ:
                return EQ[0]

    length = len(transformation_sequence)
    if length < 5:
        return representative(transformation_sequence)
    else:
        return reduce_base_form(
            representative(transformation_sequence[:4]) + transformation_sequence[4:]
        )


def rewrite_to_base_form(rich_transformation_sequence):
    """Rewrite a sequence of rich transformation as an equivalent sequence of base
    transformations."""
    base_form = []
    for transformation in rich_transformation_sequence:
        base_form.extend(BIJECTIVE_BASE_RICH_MAP[(transformation,)])
    return tuple(base_form)


def rewrite_to_rich_form(reduced_base_transformation_sequence):
    """Rewrite a *reduced* sequence of base transformations as an equivalent sequence of
    rich transformations."""
    try:
        return BIJECTIVE_BASE_RICH_MAP[reduced_base_transformation_sequence]
    except KeyError:
        raise ValueError(
            "The given sequence is not a reduced base transformation sequence:"
            + reduced_base_transformation_sequence
        )


def reduce(transformation_sequence):
    """Reduce any sequence of image transformations to the minimal equivalent
    sequence."""
    return rewrite_to_rich_form(
        reduce_base_form(rewrite_to_base_form(transformation_sequence))
    )


# Tests


def same(image1, image2):

    """Return True if the two images are exactly the same, otherwise return False"""
    return ImageChops.difference(image1, image2).getbbox() is None


def apply(transformation_sequence, image):
    """Apply the sequence of transformations to the image"""
    for op in transformation_sequence:
        image = image.transpose(op.value)
    return image


# None of the transformation sequences must occur twice
assert len(list(chain.from_iterable(ALL_EQ))) == len(set(chain.from_iterable(ALL_EQ)))

# The number of transformation sequences in all equivalence classes is the same as the
# number of all elements in 0-, 1-, 2-, 3-, and 4-fold Cartesian product of the set
# {r,f}
assert sum([len(cl) for cl in ALL_EQ]) == (2 ** 0 + 2 ** 1 + 2 ** 2 + 2 ** 3 + 2 ** 4)

# By definition, for a given equivalence class, one transformation sequence must
# produce
# exactly the same transformed image as all other transformation sequences in this
# equivalence class
an_image = Image.open("ylde.png")
for EQ in ALL_EQ:
    representative_transformation_seqence, *remaining_transformation_sequences = EQ
    representative_image = apply(representative_transformation_seqence, an_image)
    remaining_images = [
        apply(tr_seq, an_image) for tr_seq in remaining_transformation_sequences
    ]
    assert all(
        [
            same(representative_image, another_image)
            for another_image in remaining_images
        ]
    )

# No two different equivalence classes must produce the same transformed image.
for EQ1, EQ2 in combinations(ALL_EQ, 2):
    image1 = apply(EQ1[0], an_image)
    image2 = apply(EQ2[0], an_image)
    assert not same(image1, image2)

# A bijective map must always return the input value if applied twice.
for i in chain(BIJECTIVE_BASE_RICH_MAP.keys(), BIJECTIVE_BASE_RICH_MAP.values()):
    i == BIJECTIVE_BASE_RICH_MAP[BIJECTIVE_BASE_RICH_MAP[i]]
# Keys in a bijective map do not repeat, values either
len(BIJECTIVE_BASE_RICH_MAP.keys()) == len(set(BIJECTIVE_BASE_RICH_MAP.keys()))
len(BIJECTIVE_BASE_RICH_MAP.values()) == len(set(BIJECTIVE_BASE_RICH_MAP.values()))
# The set of keys and the set of values in a bijective map are the same
set(BIJECTIVE_BASE_RICH_MAP.keys()) == set(BIJECTIVE_BASE_RICH_MAP.values())

# Brute force test on all possible base transformation sequences of the size of up to
# 10 transformations. sum([2**y for y in range(10)]) = 1023 sequences.
for n_fold_product in (product((f, r), repeat=n) for n in range(10)):
    for transformation_sequence in n_fold_product:
        image_full_transformation_sequence = apply(transformation_sequence, an_image)
        image_reduced_transformation_sequence = apply(
            reduce_base_form(transformation_sequence), an_image
        )
        assert same(
            image_full_transformation_sequence, image_reduced_transformation_sequence
        )

# Brute force test on all possible rich transformation sequences of the size of up to
# 7 transformations. sum([5**y for y in range(7)]) = 19531 sequences.
counter = 0
for n_fold_product in (product((t for t in T), repeat=n) for n in range(7)):
    for transformation_sequence in n_fold_product:
        image_full_transformation_sequence = apply(transformation_sequence, an_image)
        image_reduced_transformation_sequence = apply(
            reduce(transformation_sequence), an_image
        )
        assert same(
            image_full_transformation_sequence, image_reduced_transformation_sequence
        )
        counter += 1
print(counter)
