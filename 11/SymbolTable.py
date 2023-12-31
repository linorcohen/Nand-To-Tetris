"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.index_table = {"STATIC": 0, "FIELD": 0, "ARG": 0, "VAR": 0}

        self.cur_symbol_table = {}

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        for key in self.index_table.keys():
            self.index_table[key] = 0

        self.cur_symbol_table.clear()

    def define(self, name: str, var_type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            var_type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        self.cur_symbol_table[name] = [var_type, kind.upper(), self.index_table[kind.upper()]]
        self.index_table[kind.upper()] += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        var_count = 0
        for value in self.cur_symbol_table.values():
            if value[1] == kind.upper():
                var_count += 1
        return var_count

    def kind_of(self, name: str) -> typing.Optional[typing.Any]:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if name not in self.cur_symbol_table:
            return None
        return self.cur_symbol_table[name][1]

    def type_of(self, name: str) -> typing.Optional[typing.Any]:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name not in self.cur_symbol_table:
            return None
        return self.cur_symbol_table[name][0]

    def index_of(self, name: str) -> typing.Optional[typing.Any]:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name not in self.cur_symbol_table:
            return None
        return self.cur_symbol_table[name][2]
