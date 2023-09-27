"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class VMWriter:
    """
    Writes VM commands into a file. Encapsulates the VM command syntax.
    """

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Creates a new file and prepares it for writing VM commands."""
        self.output_file = output_stream

        self.segment_table = {"CONST": "constant", "ARG": "argument", "VAR": "local",
                              "STATIC": "static", "FIELD": "this", "THAT": "that",
                              "POINTER": "pointer", "TEMP": "temp"}

    def write_push(self, segment: str, index: int) -> None:
        """Writes a VM push command.

        Args:
            segment (str): the segment to push to, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"
            index (int): the index to push to.
        """
        self.output_file.write("""push {segment} {index}\n""".format(segment=self.segment_table[segment],
                                                                     index=index))

    def write_pop(self, segment: str, index: int) -> None:
        """Writes a VM pop command.

        Args:
            segment (str): the segment to pop from, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP".
            index (int): the index to pop from.
        """
        self.output_file.write("""pop {segment} {index}\n""".format(segment=self.segment_table[segment],
                                                                    index=index))

    def write_arithmetic(self, command: str) -> None:
        """Writes a VM arithmetic command.

        Args:
            command (str): the command to write, can be "ADD", "SUB", "NEG", 
            "EQ", "GT", "LT", "AND", "OR", "NOT", "SHIFTLEFT", "SHIFTRIGHT".
        """
        if command.split()[0] == "call":
            self.output_file.write("""{command}\n""".format(command=command))
        else:
            self.output_file.write("""{command}\n""".format(command=command.lower()))

    def write_label(self, label: str) -> None:
        """Writes a VM label command.

        Args:
            label (str): the label to write.
        """
        self.output_file.write("""label {label}\n""".format(label=label.upper()))

    def write_goto(self, label: str) -> None:
        """Writes a VM goto command.

        Args:
            label (str): the label to go to.
        """
        self.output_file.write("""goto {label}\n""".format(label=label.upper()))

    def write_if(self, label: str) -> None:
        """Writes a VM if-goto command.

        Args:
            label (str): the label to go to.
        """
        self.output_file.write("""if-goto {label}\n""".format(label=label.upper()))

    def write_call(self, name: str, n_args: int) -> None:
        """Writes a VM call command.

        Args:
            name (str): the name of the function to call.
            n_args (int): the number of arguments the function receives.
        """
        self.output_file.write("""call {name} {n_args}\n""".format(name=name, n_args=n_args))

    def write_function(self, name: str, n_locals: int) -> None:
        """Writes a VM function command.

        Args:
            name (str): the name of the function.
            n_locals (int): the number of local variables the function uses.
        """
        self.output_file.write("""function {name} {n_locals}\n""".format(name=name, n_locals=n_locals))

    def write_return(self) -> None:
        """Writes a VM return command."""
        self.output_file.write("return\n")

    def close(self) -> None:
        self.output_file.close()
