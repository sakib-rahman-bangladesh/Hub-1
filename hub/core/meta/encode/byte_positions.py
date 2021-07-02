from re import L
from typing import Tuple
import numpy as np


POSITION_ENCODING_DTYPE = np.uint64

NUM_BYTES_INDEX = 0
START_BYTE_INDEX = 1
LAST_INDEX_INDEX = 2


class BytePositionsEncoder:
    def __init__(self, encoded_byte_positions=None):
        self._encoded = encoded_byte_positions

    @property
    def num_samples(self) -> int:
        if self._encoded is None:
            return 0
        return int(self._encoded[-1, LAST_INDEX_INDEX] + 1)

    def num_bytes_encoded_under_row(self, row_index: int) -> int:
        if self._encoded is None:
            return 0

        if row_index < 0:
            row_index = len(self._encoded) + row_index

        row = self._encoded[row_index]

        if row_index == 0:
            previous_last_index = -1
        else:
            previous_last_index = self._encoded[row_index - 1, LAST_INDEX_INDEX]

        num_samples = row[LAST_INDEX_INDEX] - previous_last_index
        num_bytes_for_entry = num_samples * row[NUM_BYTES_INDEX]
        return int(num_bytes_for_entry + row[START_BYTE_INDEX])

    @property
    def nbytes(self):
        if self._encoded is None:
            return 0
        return self._encoded.nbytes

    @property
    def array(self):
        return self._encoded

    def add_byte_position(self, num_bytes_per_sample: int, num_samples: int):
        if num_samples <= 0:
            raise ValueError(f"`num_samples` should be > 0. Got {num_samples}.")

        if num_bytes_per_sample < 0:
            raise ValueError(f"`num_bytes` must be >= 0. Got {num_bytes_per_sample}.")

        if self.num_samples != 0:
            last_entry = self._encoded[-1]
            last_nb = last_entry[NUM_BYTES_INDEX]

            if last_nb == num_bytes_per_sample:
                self._encoded[-1, LAST_INDEX_INDEX] += num_samples

            else:
                last_index = last_entry[LAST_INDEX_INDEX]

                sb = self.num_bytes_encoded_under_row(-1)

                entry = np.array(
                    [[num_bytes_per_sample, sb, last_index + num_samples]],
                    dtype=POSITION_ENCODING_DTYPE,
                )
                self._encoded = np.concatenate([self._encoded, entry], axis=0)

        else:
            self._encoded = np.array(
                [[num_bytes_per_sample, 0, num_samples - 1]],
                dtype=POSITION_ENCODING_DTYPE,
            )

    def __getitem__(self, sample_index: int) -> Tuple[int, int]:
        if self.num_samples == 0:
            raise IndexError(
                f"Index {sample_index} is out of bounds for an empty byte position encoding."
            )

        if sample_index < 0:
            sample_index = (self.num_samples) + sample_index

        idx = np.searchsorted(self._encoded[:, -1], sample_index)

        entry = self._encoded[idx]

        index_bias = 0
        if idx >= 1:
            index_bias = self._encoded[idx - 1][LAST_INDEX_INDEX] + 1

        nb = entry[NUM_BYTES_INDEX]
        lsb = entry[START_BYTE_INDEX]

        sb = lsb + (sample_index - index_bias) * nb
        eb = sb + nb
        return int(sb), int(eb)