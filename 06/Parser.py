"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """
    A_COMMAND = "A_COMMAND"
    C_COMMAND = "C_COMMAND"
    L_COMMAND = "L_COMMAND"
    INITIAL_VAL = -1
    COMMENT = "//"
    NULL = "null"
    EMPTY = ""
    NOT_FOUND = -1

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.input_lines = input_file.read().splitlines()
        self.n = self.INITIAL_VAL
        self.command_idx = self.INITIAL_VAL
        self.cur_instruction = self.EMPTY

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        while len(self.input_lines) - 1 != self.n:
            self.n += 1
            self.cur_instruction = self.input_lines[self.n].strip(). \
                replace(" ", "")
            if self.cur_instruction != self.EMPTY and self.cur_instruction[
                                                      0:2] != self.COMMENT:
                return True
        return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        if self.cur_instruction[0] != "(":  # not L_COMMAND
            self.command_idx += 1
        # remove inline comments:
        inline_comment_idx = self.cur_instruction.find(self.COMMENT)
        if inline_comment_idx != self.NOT_FOUND:
            self.cur_instruction = self.cur_instruction[0:inline_comment_idx]
        # remove all additional tags:
        self.cur_instruction = ''.join(self.cur_instruction.split())

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        first_param = self.cur_instruction[0]
        if first_param == "(":
            return self.L_COMMAND
        elif first_param == "@":
            return self.A_COMMAND
        return self.C_COMMAND

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        command_type = self.cur_instruction[0]
        symbol = self.cur_instruction[1:]
        if command_type == "@":  # A_COMMAND symbol
            return symbol
        return symbol[:-1]  # L_COMMAND symbol

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        dest_idx = self.cur_instruction.find("=")
        if dest_idx == self.NOT_FOUND:
            return self.NULL
        return self.cur_instruction[0:dest_idx]

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        return re.split(';', re.split('=', self.cur_instruction)[-1])[0]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        jump_idx = self.cur_instruction.find(";")
        if jump_idx == self.NOT_FOUND or self.cur_instruction[jump_idx + 1:] == '':
            return self.NULL
        return self.cur_instruction[jump_idx + 1:]
