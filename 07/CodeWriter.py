"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import textwrap
import os


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    STATIC_ADDR = 16
    TEMP_ADDR = 5

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_file = output_stream
        self.filename = ""
        self.counter = 0
        self.segment_table = {"local": "LCL", "argument": "ARG",
                              "this": "THIS", "that": "THAT",
                              "static": self.STATIC_ADDR,
                              "temp": self.TEMP_ADDR}

        self.jmp_table = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}

        self.operator_table = {"add": "+", "sub": "-", "neg": "-", "not": "!",
                               "shiftright": ">>", "shiftleft": "<<",
                               "and": "&", "or": "|"}

    def __write_command_comment(self, command: str) -> None:
        """
        write a command comment before its assembly code
        :param command: a command
        """
        self.output_file.write("// " + command)

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.filename, input_extension = \
            os.path.splitext(os.path.basename(filename))

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        self.__write_command_comment(command)
        text = ""
        if command in {"sub", "add"}:
            text = self.__sub_add_commands(command)
        elif command in {"neg", "not"}:
            text = self.__neg_not_commands(command)
        elif command in {"eq", "lt", "gt"}:
            text = self.__boolean_commands(command)
        elif command in {"shiftleft", "shiftright"}:
            text = self.__shift_commands(command)
        elif command in {"and", "or"}:
            text = self.__and_or_commands(command)
        self.output_file.write(textwrap.dedent(text))

    def __sub_add_commands(self, command: str) -> str:
        """
        returns the assembly code for sub or add VM command.
        :param command: (str) an sub or add command.
        :return: assembly code translation of the command
        """
        return """
        @SP
        M=M-1
        A=M
        D=M
        A=A-1
        D=M{operator}D
        M=D
        """.format(operator=self.operator_table[command])

    def __neg_not_commands(self, command: str) -> str:
        """
        returns the assembly code for neg or not VM command.
        :param command: (str) an neg or not command.
        :return: assembly code translation of the command
        """
        return """
        @SP
        A=M-1
        M={operator}M
        """.format(operator=self.operator_table[command])

    def __boolean_commands(self, command: str) -> str:
        """
        returns the assembly code for lt,gt or eq VM command.
        :param command: (str) an lt,gt or eq command.
        :return: assembly code translation of the command
        """
        self.counter += 1
        return """
        @SP
        M=M-1
        A=M
        D=M
        @NEG_{i}
        D;JLT
        @SP
        A=M-1
        D=M
        @POS_NEG_{i}
        D;JLT
        @SAME_SIGN_{i}
        0;JMP
        (NEG_{i})
        @SP
        A=M-1
        D=M
        @SAME_SIGN_{i}
        D;JLT
        D=1
        @CHECK_COMMAND_{i}
        0;JMP
        (POS_NEG_{i})
        D=-1
        @CHECK_COMMAND_{i}
        0;JMP
        (SAME_SIGN_{i})
        @SP
        A=M
        D=M
        @SP
        A=M-1
        D=M-D
        (CHECK_COMMAND_{i})
        @TRUE_{command}_{i}
        D;{command_jmp}
        @SP
        A=M-1
        M=0
        @{command}_{i}
        0;JMP
        (TRUE_{command}_{i})
        @SP
        A=M-1
        M=-1
        ({command}_{i})
        """.format(sub=self.__sub_add_commands("sub"), command=command.upper(),
                   command_jmp=self.jmp_table[command], i=self.counter)

    def __shift_commands(self, command: str) -> str:
        """
        returns the assembly code for shiftleft or shiftright VM command.
        :param command: (str) an shiftleft or shiftright command.
        :return: assembly code translation of the command
        """
        return """
        @SP
        A=M-1
        M=M{operator}
        """.format(operator=self.operator_table[command])

    def __and_or_commands(self, command: str) -> str:
        """
        returns the assembly code for and or or VM command.
        :param command: (str) an and or or command.
        :return: assembly code translation of the command
        """
        return """
        @SP
        M=M-1
        A=M
        D=M
        A=A-1
        M=D{operator}M
        """.format(operator=self.operator_table[command])

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        self.__write_command_comment(
            f"{command[2:].lower()} {segment} {index}")
        text = ""
        if command == "C_PUSH":
            text = self.__get_push_command(segment, index)
        elif command == "C_POP":
            text = self.__get_pop_command(segment, index)
        self.output_file.write(textwrap.dedent(text))

    def __get_push_command(self, segment: str, index: int) -> str:
        """
        returns the assembly code for the given push command
        :param segment: the memory segment to operate on.
        :param index: the index in the memory segment.
        :return: assembly code translation of the command
        """
        if segment in {"local", "argument", "this", "that", "temp"}:
            return self.__lcl_arg_this_that_temp_push(segment, index)
        elif segment == "static":
            return self.__static_push(index)
        elif segment == "constant":
            return self.__constent_push(index)
        elif segment == "pointer":
            return self.__pointer_push(index)

    def __get_pop_command(self, segment: str, index: int) -> str:
        """
        returns the assembly code for the given pop command
        :param segment: the memory segment to operate on.
        :param index: the index in the memory segment.
        :return: assembly code translation of the command
        """
        if segment in {"local", "argument", "this", "that", "temp"}:
            return self.__lcl_arg_this_that_temp_pop(segment, index)
        elif segment == "static":
            return self.__static_pop(index)
        elif segment == "pointer":
            return self.__pointer_pop(index)

    def __lcl_arg_this_that_temp_push(self, segment: str, index: int) -> str:
        """
        returns the assembly code for push local, argument, this, that,
        temp VM command.
        :param segment: the memory segment to operate on.
        :param index:  the index in the memory segment.
        :return: assembly code translation of the command
        """
        return """
        @{segmentPointer}
        D={is_temp}
        @{i}
        A=D+A
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        """.format(segmentPointer=self.segment_table[segment], i=index,
                   is_temp=(lambda x: "A" if x == "temp" else "M")(segment))

    def __lcl_arg_this_that_temp_pop(self, segment: str, index: int) -> str:
        """
        returns the assembly code for pop local, argument, this, that,
        temp VM command.
        :param segment: the memory segment to operate on.
        :param index:  the index in the memory segment.
        :return: assembly code translation of the command
        """
        return """
        @{segmentPointer}
        D={is_temp}
        @{i}
        D=D+A
        @R13
        M=D
        @SP
        M=M-1
        A=M
        D=M
        @R13
        A=M
        M=D
        """.format(segmentPointer=self.segment_table[segment], i=index,
                   is_temp=(lambda x: "A" if x == "temp" else "M")(segment))

    def __static_push(self, index: int) -> str:
        """
        returns the assembly code for push static VM command.
        :param index:  the index in the memory segment.
        :return: assembly code translation of the command
        """
        return """
        @{file_name}.{i}
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        """.format(file_name=self.filename, i=index)

    def __static_pop(self, index: int) -> str:
        """
        returns the assembly code for pop static VM command.
        :param index: the index in the memory segment.
        :return: assembly code translation of the command
        """
        return """
        @SP
        M=M-1
        A=M
        D=M
        @{file_name}.{i}
        M=D
        """.format(file_name=self.filename, i=index)

    def __constent_push(self, index: int) -> str:
        """
        returns the assembly code for push constant VM command.
        :param index:  the index in the memory segment.
        :return: assembly code translation of the command
        """
        return """
        @{i}
        D=A
        @SP
        A=M
        M=D
        @SP
        M=M+1
        """.format(i=index)

    def __pointer_push(self, index: int) -> str:
        """
        returns the assembly code for push pointer (0/1 == THIS/THAT)
        VM command.
        :param index: the index in the memory segment.
        :return: assembly code translation of the command
        """
        return """
        @THIS
        D=A
        @{i}
        A=D+A
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        """.format(i=index)

    def __pointer_pop(self, index: int) -> str:
        """
        returns the assembly code for pop pointer (0/1 == THIS/THAT)
        VM command.
        :param index: the index in the memory segment.
        :return: assembly code translation of the command
        """
        return """
        @THIS
        D=A
        @{i}
        D=D+A
        @R13
        M=D
        @SP
        M=M-1
        A=M
        D=M
        @R13
        A=M
        M=D
        """.format(i=index)

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        pass

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        pass

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        pass

    def close(self) -> None:
        """
        close the open file
        """
        self.output_file.close()
