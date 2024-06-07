def layout(
    encoder_ccw,
    encoder_cw,
    # fmt: off
          up,
    left, middle, right,
          down,
    F00, F01,
    F10, F11,
    F20, F21,
    F30, F31,
    # fmt: on
) -> tuple:
    return (
        # fmt: off
        up,    F00, F01,
        right, F10, F11,
        down,  F20, F21,
        left,  F30, F31,
        # fmt: on
        middle,
        encoder_ccw,
        encoder_cw,
    )


INDEX_ENCODER_MIDDLE = 12
INDEX_ENCODER_CCW = 13
INDEX_ENCODER_CW = 14
LAYOUT_SIZE = 15
