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
    EMPTY = ""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_file = output_stream
        self.filename = self.EMPTY
        self.function = self.EMPTY
        self.return_idx = 0
        self.counter = 0
        self.segment_table = {"local": "LCL", "argument": "ARG",
                              "this": "THIS", "that": "THAT",
                              "static": self.STATIC_ADDR,
                              "temp": self.TEMP_ADDR}

        self.jmp_table = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}

        self.operator_table = {"add": "+", "sub": "-", "neg": "-", "not": "!",
                               "shiftright": ">>", "shiftleft": "<<",
                               "and": "&", "or": "|"}

    def write_command_comment(self, command: str) -> None:
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
        self.write_command_comment(command)
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
        @{file_name}.NEG_{command}_{i}
        D;JLT
        @SP
        A=M-1
        D=M
        @{file_name}.POS_NEG_{command}_{i}
        D;JLT
        @{file_name}.SAME_SIGN_{command}_{i}
        0;JMP
        ({file_name}.NEG_{command}_{i})
        @SP
        A=M-1
        D=M
        @{file_name}.SAME_SIGN_{command}_{i}
        D;JLT
        D=1
        @{file_name}.CHECK_COMMAND_{command}_{i}
        0;JMP
        ({file_name}.POS_NEG_{command}_{i})
        D=-1
        @{file_name}.CHECK_COMMAND_{command}_{i}
        0;JMP
        ({file_name}.SAME_SIGN_{command}_{i})
        @SP
        A=M
        D=M
        @SP
        A=M-1
        D=M-D
        ({file_name}.CHECK_COMMAND_{command}_{i})
        @{file_name}.TRUE_{command}_{i}
        D;{command_jmp}
        @SP
        A=M-1
        M=0
        @{file_name}.{command}_{i}
        0;JMP
        ({file_name}.TRUE_{command}_{i})
        @SP
        A=M-1
        M=-1
        ({file_name}.{command}_{i})
        """.format(file_name=self.filename, sub=self.__sub_add_commands("sub"), command=command.upper(),
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
        self.write_command_comment(
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
        self.write_command_comment(f'label {label}')
        self.output_file.write(textwrap.dedent("""
        ({label})
        """.format(label=f'{self.filename}.{self.function}${label}')))

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        self.write_command_comment(f'goto {label}')
        self.output_file.write(textwrap.dedent("""
        @{label}
        0;JMP
        """).format(label=f'{self.filename}.{self.function}${label}'))

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        self.write_command_comment(f'if-goto {label}')
        self.output_file.write(textwrap.dedent("""
        @SP
        M=M-1
        A=M
        D=M
        @{label}
        D;JNE
        """).format(label=f'{self.filename}.{self.function}${label}'))

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
        self.function = function_name
        self.write_command_comment(f'function {function_name} {n_vars}')
        self.output_file.write(textwrap.dedent("""
        ({label})
        """.format(label=function_name)))
        for i in range(n_vars):
            self.output_file.write(textwrap.dedent("""
        @SP
        A=M
        M=0
        @SP
        M=M+1
        """))

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
        return_label = f'{self.filename}.{function_name}$ret.{self.return_idx}'
        self.return_idx += 1
        self.write_command_comment(f'call {function_name} {n_args}')
        self.output_file.write(
            textwrap.dedent(self.__set_call_saved_params(return_label) + """
        @{nArgs}
        D=A     
        @5
        D=D+A
        @SP
        D=M-D 
        @ARG
        M=D      
        @SP
        D=M
        @LCL
        M=D
        @{label}
        0;JMP
        ({return_label})
        """.format(nArgs=n_args, label=function_name,
                   return_label=return_label)))

    def __set_call_saved_params(self, return_label: str) -> str:
        """
        this function set call command parameters at the saved places
        :param return_label: return label of the call
        :return: asm code for the saved params
        """
        return \
            """{r_address}{save_lcl}{save_arg}{save_this}{save_that}""".format(
                r_address=self.__get_call_push_code(return_label, True),
                save_lcl=self.__get_call_push_code("local", False),
                save_arg=self.__get_call_push_code("argument", False),
                save_this=self.__get_call_push_code("this", False),
                save_that=self.__get_call_push_code("that", False))

    def __get_call_push_code(self, segment: str, is_label: bool) -> str:
        """
        this function gets call command push asm code
        :param segment: call segment
        :param is_label: true if label, false otherwise
        :return: asm code
        """
        return """
        @{segmentPointer}
        D={is_label}
        @SP
        A=M
        M=D
        @SP
        M=M+1""".format(segmentPointer=(
            lambda x: segment if x else self.segment_table[segment])(is_label),
                        is_label=(lambda x: "A" if x else "M")(is_label))

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        self.write_command_comment('return')
        self.output_file.write(textwrap.dedent("""
        @LCL
        D=M
        @R14
        M=D
        @5
        A=D-A
        D=M
        @R15
        M=D
        @SP
        A=M-1
        D=M
        @ARG
        A=M
        M=D
        @ARG
        D=M
        @SP
        M=D+1""" + self.__set_return_params() + """
        @R15
        A=M
        0;JMP
        """))

    # def write_return(self) -> None:
    #     """Writes assembly code that affects the return command."""
    #     self.write_command_comment('return')
    #     self.output_file.write(textwrap.dedent("""
    #     @LCL
    #     D=M
    #     @R14
    #     M=D
    #     @5
    #     A=D-A
    #     D=M
    #     @R15
    #     M=D
    #
    #     //pop argument 0
    #     @2
    #     D=M
    #     @0
    #     D=D+A
    #     @R13
    #     M=D
    #     @SP
    #     M=M-1
    #     A=M
    #     D=M
    #     @R13
    #     A=M
    #     M=D
    #     @2
    #     D=M
    #     @SP
    #     M=D+1
    #     @R14
    #     A=M-1
    #     D=M
    #     @4
    #     M=D
    #     @2
    #     D=A
    #     @R14
    #     A=M-D
    #     D=M
    #     @3
    #     M=D
    #     @3
    #     D=A
    #     @R14
    #     A=M-D
    #     D=M
    #     @2
    #     M=D
    #     @4
    #     D=A
    #     @R14
    #     A=M-D
    #     D=M
    #     @1
    #     M=D
    #     @R15
    #     A=M
    #     0;JMP"""))

    def __set_return_params(self) -> str:
        """
        this function sets the return parameters
        :return: asm code of the return params
        """
        return """{save_that}{save_this}{save_arg}{save_local}""".format(
            save_that=self.__get_return_params("that"),
            save_this=self.__get_return_params("this"),
            save_arg=self.__get_return_params("argument"),
            save_local=self.__get_return_params("local"))

    def __get_return_params(self, segment: str) -> str:
        """
        this function gets the return parameters
        @segment: the return segment
        :return: asm code of the return params
        """
        return """
        @R14
        M=M-1
        A=M
        D=M
        @{segmentPointer}
        M=D""".format(segmentPointer=self.segment_table[segment])

    def bootstrap_init(self) -> None:
        """
        bootstrap initializer
        :return: asm code of the bootstrap initializer
        """
        self.write_command_comment(f'bootstrap initialize')
        self.output_file.write(textwrap.dedent("""
        @256
        D=A
        @SP
        M=D
        """))
        self.write_call("Sys.init", 0)

    def close(self) -> None:
        """
        close the open file
        """
        self.output_file.close()
