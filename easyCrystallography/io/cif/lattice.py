from __future__ import annotations

__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

#  SPDX-FileCopyrightText: 2023 easyCrystallography contributors <crystallography@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2022-2023  Contributors to the easyCore project <https://github.com/easyScience/easyCrystallography>

from typing import List, NoReturn, TYPE_CHECKING, ClassVar, Tuple

from .template import CIF_Template, gemmi
from easyCrystallography.Components.Lattice import Lattice as _Lattice

if TYPE_CHECKING:
    from easyCore.Utils.typing import B


class Lattice(CIF_Template):

    _CIF_SECTION_NAME: ClassVar[str] = "_cell"
    _CIF_CONVERSIONS: ClassVar[List[Tuple[str, str]]] = [
        ("length_a", "_length_a"),
        ("length_b", "_length_b"),
        ("length_c", "_length_c"),
        ("angle_alpha", "_angle_alpha"),
        ("angle_beta", "_angle_beta"),
        ("angle_gamma", "_angle_gamma"),
    ]

    def __init__(self, reference_class=_Lattice):
        super().__init__()
        self._CIF_CLASS = reference_class

    def from_cif_block(self, block: gemmi.cif.Block) -> B:
        kwargs = {}
        errors = {}
        is_fixed = {}
        for item in self._CIF_CONVERSIONS:
            value = block.find_pair_item(self._CIF_SECTION_NAME + item[1])
            V, E, F = self.string_to_variable(value.pair[1])
            if E:
                errors[item[0]] = E
            if F is not None and not F:
                is_fixed[item[0]] = F
            kwargs[item[0]] = V
        obj = self._CIF_CLASS(**kwargs)
        for error in errors.keys():
            setattr(getattr(obj, error), 'error', errors[error])
        for atr in is_fixed.keys():
            setattr(getattr(obj, atr), 'fixed', is_fixed[atr])
        return obj

    def add_to_cif_block(self, obj: B, block: gemmi.cif.Block) -> NoReturn:
        for item in self._CIF_CONVERSIONS:
            value = getattr(obj, item[0])
            block.set_pair(self._CIF_SECTION_NAME + item[1], self.variable_to_string(value))

    def from_cif_string(self, cif_string: str) -> List[B]:

        if "data_" not in cif_string:
            cif_string = "data_temp\n" + cif_string

        cif_blocks = gemmi.cif.read_string(cif_string)
        objs = []
        for block in cif_blocks:
            objs.append(self.from_cif_block(block))
        return objs
