"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code

INITIAL_ADDRESS = 16
ZERO_FILL = 15
NOT_FOUND = -1
LEFT_SHIFT = "<<"
RIGHT_SHIFT = ">>"
SHIFT_CODE = "101"
C_CODE = "111"
A_CODE = "0"


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Initialization
    first_parser = Parser(input_file)
    input_file.seek(0)
    sec_parser = Parser(input_file)
    symbol_table = SymbolTable()
    available_address_idx = INITIAL_ADDRESS

    # First Pass
    while first_parser.has_more_commands():
        first_parser.advance()
        if first_parser.command_type() == first_parser.L_COMMAND:
            l_symbol = first_parser.symbol()
            symbol_table.add_entry(l_symbol, first_parser.command_idx + 1)

    # Second Pass
    while sec_parser.has_more_commands():
        sec_parser.advance()
        # If the instruction is @ symbol
        if sec_parser.command_type() == sec_parser.A_COMMAND:
            cur_address, address_idx = get_cur_address(available_address_idx, sec_parser,
                                                       symbol_table)
            available_address_idx = address_idx
            # Translates the symbol to its binary value
            output_file.write(
                A_CODE + bin(int(cur_address))[2:].zfill(ZERO_FILL) + '\n')

        # If the instruction is dest =comp ; jump
        elif sec_parser.command_type() == sec_parser.C_COMMAND:
            output_file.write(get_full_c_command(sec_parser))


def get_full_c_command(sec_parser: Parser) -> str:
    """
    This function returns the full binary command for type C_COMMAND
    :param sec_parser: current parser
    :return: string represent the binary code of the current C_COMMAND
    """
    comp = sec_parser.comp()
    full_command = Code.comp(comp) + Code.dest(sec_parser.dest()) + Code.jump(
        sec_parser.jump()) + '\n'
    if comp.find(LEFT_SHIFT) != NOT_FOUND or comp.find(
            RIGHT_SHIFT) != NOT_FOUND:
        return SHIFT_CODE + full_command
    return C_CODE + full_command


def get_cur_address(address_idx, sec_parser, symbol_table):
    """
    get the current symbol address from the symbol table
    :param address_idx: current available address
    :param sec_parser: secondary parser
    :param symbol_table: the symbol table to fetch from
    :return: the symbol address, current available address
    """
    cur_symbol = sec_parser.symbol()
    if not cur_symbol.isnumeric():
        # If symbol is not in the symbol table, adds it
        if not symbol_table.contains(cur_symbol):
            symbol_table.add_entry(cur_symbol, address_idx)
            address_idx += 1
        return symbol_table.get_address(cur_symbol), address_idx
    return cur_symbol, address_idx


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
