"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import JackTokenizer
from SymbolTable import SymbolTable
import VMWriter


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    FUNCTION = "function"
    CONSTRUCTOR = "constructor"
    METHOD = "method"
    STATIC = "static"
    FIELD = "field"
    RETURN = "return"
    WHILE = "while"
    LET = "let"
    DO = "do"
    IF = "if"
    ELSE = "else"

    KEYWORD = "KEYWORD"
    SYMBOL = "SYMBOL"
    IDENTIFIER = "IDENTIFIER"
    INT_CONST = "INT_CONST"
    STRING_CONST = "STRING_CONST"

    def __init__(self, input_stream: "JackTokenizer", class_symbol_table: "SymbolTable",
                 vm_writer: "VMWriter", output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.class_symbol_table = class_symbol_table
        self.vm_writer = vm_writer
        self.tokenizer = input_stream
        self.output_stream = output_stream

        self.op_terms = {"+": "ADD", "-": "SUB", "*": "call Math.multiply 2", "/": "call Math.divide 2",
                         "&": "AND", "|": "OR", "<": "LT", ">": "GT", "=": "EQ"}
        self.unary_op_terms = {"^": "SHIFTLEFT", "#": "SHIFTRIGHT", "-": "NEG", "~": "NOT"}

        self.class_name = ""
        self.counter = 0
        self.subroutine_symbol_table = SymbolTable()

    def __advance_tokenizer(self) -> None:
        """
        this method advance the tokenizer if has more tokens
        """
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

    def __get_current_token_and_advance(self) -> str:
        """
        this method advance the token and get the current token
        :return: Tuple(token, token tag type)
        """
        self.__advance_tokenizer()
        return self.__get_current_token()

    def __get_current_token(self) -> str:
        """
        this method return the tuple of the current token and the current token type tag.
        :return: Tuple(token, token tag type)
        """
        t_type = self.tokenizer.token_type()
        if t_type == self.KEYWORD:
            return self.tokenizer.keyword()
        elif t_type == self.SYMBOL:
            return self.tokenizer.symbol()
        elif t_type == self.IDENTIFIER:
            return self.tokenizer.identifier()
        elif t_type == self.INT_CONST:
            return str(self.tokenizer.int_val())
        elif t_type == self.STRING_CONST:
            return self.tokenizer.string_val()

    def __get_var_info_from_table(self, var_name: str) -> typing.Tuple[str, str, str]:
        """
        this method return the var info from its symbol table.
        :param var_name: variable name
        :return: variable type, variable kind, variable index
        """
        # symbol in class table
        if self.subroutine_symbol_table.kind_of(var_name) is not None:
            # symbol in subroutine table
            return self.subroutine_symbol_table.type_of(var_name), \
                   self.subroutine_symbol_table.kind_of(var_name), \
                   self.subroutine_symbol_table.index_of(var_name)
        return self.class_symbol_table.type_of(var_name), self.class_symbol_table.kind_of(
            var_name), self.class_symbol_table.index_of(var_name)

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # class
        self.__get_current_token_and_advance()
        # className
        self.class_name = self.__get_current_token_and_advance()
        # {
        self.__get_current_token_and_advance()
        # classVarDec -> *
        token = self.__get_current_token_and_advance()
        while token in {self.FIELD, self.STATIC}:
            self.compile_class_var_dec()
            token = self.__get_current_token_and_advance()
        # subroutineDec -> *
        while token in {self.METHOD, self.CONSTRUCTOR, self.FUNCTION}:
            self.compile_subroutine()
            token = self.__get_current_token_and_advance()
        # }

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # field or static
        kind = self.__get_current_token()
        # type
        token = self.__get_current_token_and_advance()
        var_type = token
        # varName -> *
        while token != ";":
            # varName
            name = self.__get_current_token_and_advance()
            # add to class_table
            self.class_symbol_table.define(name, var_type, kind)
            # symbol
            token = self.__get_current_token_and_advance()

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field.
        """
        # keyword - method, function, or constructor.
        subroutine_type = self.__get_current_token()
        # identifier - return type
        self.__get_current_token_and_advance()
        # identifier - name
        subroutine_name = self.__get_current_token_and_advance()
        # reset the subroutine symbol table
        self.subroutine_symbol_table.start_subroutine()
        # add the object this to subroutine table
        if subroutine_type == self.METHOD:
            self.subroutine_symbol_table.define("this", self.class_name, "ARG")
        # (
        self.__get_current_token_and_advance()
        # parameter list
        self.compile_parameter_list()
        # )
        self.__get_current_token()
        # subroutine body
        self.__compile_subroutine_body(subroutine_name, subroutine_type)

    def __compile_subroutine_body(self, subroutine_name: str, subroutine_type: str) -> None:
        """
        this method compile a subroutine body
        """
        # {
        self.__get_current_token_and_advance()
        n = 0
        # var -> *
        var_type = self.__get_current_token_and_advance()
        while var_type == "var":
            n += self.compile_var_dec()
            var_type = self.__get_current_token_and_advance()
        # function className.subroutineName n
        self.vm_writer.write_function(f"""{self.class_name}.{subroutine_name}""", n)
        if subroutine_type == self.CONSTRUCTOR:
            # push const nField
            self.vm_writer.write_push("CONST", self.class_symbol_table.var_count(self.FIELD))
            # call Memory.alloc 1
            self.vm_writer.write_call("Memory.alloc", 1)
            # pop pointer 0
            self.vm_writer.write_pop("POINTER", 0)
        if subroutine_type == self.METHOD:
            # push argument 0
            self.vm_writer.write_push("ARG", 0)
            # pop pointer 0
            self.vm_writer.write_pop("POINTER", 0)
        # statements
        self.compile_statements(subroutine_type)
        # }
        self.__get_current_token()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        is_first = True
        # varName -> *
        var_type = self.__get_current_token_and_advance()
        while var_type != ")":
            if is_first:
                name = self.__get_current_token_and_advance()
                # add to subroutine table
                self.subroutine_symbol_table.define(name, var_type, "ARG")
                var_type = self.__get_current_token_and_advance()
                is_first = False
            else:
                var_type = self.__get_current_token_and_advance()
                name = self.__get_current_token_and_advance()
                # add to subroutine table
                self.subroutine_symbol_table.define(name, var_type, "ARG")
                var_type = self.__get_current_token_and_advance()

    def compile_var_dec(self) -> int:
        """Compiles a var declaration."""
        # keyword
        kind = self.__get_current_token()
        # identifier
        token = self.__get_current_token_and_advance()
        var_type = token
        n = 0
        # varName -> *
        while token != ";":
            # identifier
            name = self.__get_current_token_and_advance()
            # add to subroutine table
            self.subroutine_symbol_table.define(name, var_type, kind.upper())
            n += 1
            # symbol
            token = self.__get_current_token_and_advance()
        return n

    def __compile_string(self, string_value: str) -> None:
        """
        this method compile a string constance
        :param string_value: the string variable
        """
        # push const length
        self.vm_writer.write_push("CONST", len(string_value))
        # call string.new
        self.vm_writer.write_call("String.new", 1)
        for char in string_value:
            # push const char
            self.vm_writer.write_push("CONST", str(ord(char)))
            # call string.appendChar
            self.vm_writer.write_call("String.appendChar", 2)

    def compile_statements(self, subroutine_type: str) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        token = self.__get_current_token()
        while token != "}":
            if token == self.IF:
                self.compile_if(subroutine_type)
                token = self.__get_current_token()
            else:
                if token == self.DO:
                    self.compile_do()
                elif token == self.LET:
                    self.compile_let()
                elif token == self.WHILE:
                    self.compile_while(subroutine_type)
                elif token == self.RETURN:
                    self.compile_return(subroutine_type)
                token = self.__get_current_token_and_advance()

    def __subroutine_call_format(self, obj_name: str, is_term: bool) -> None:
        """
        this method compile the subroutine call format
        """
        function_call_name = obj_name
        is_method = 0
        # . -> ?
        symbol = self.__get_current_token()
        if symbol == ".":
            var_type, var_kind, var_index = self.__get_var_info_from_table(obj_name)
            if var_type is not None and var_kind is not None and var_kind is not None:  # varName
                if not is_term:
                    # push obj
                    self.vm_writer.write_push(var_kind, var_index)
                is_method = 1
                function_call_name = var_type
            # functionName
            function_name = self.__get_current_token_and_advance()
            function_call_name += symbol + function_name
            # ( -> ?
            self.__get_current_token_and_advance()
        else:
            self.vm_writer.write_push("POINTER", 0)
            function_call_name = self.class_name + "." + obj_name
            is_method = 1
        # (
        # expression list
        self.__get_current_token_and_advance()
        n = self.compile_expression_list()
        # )
        self.__get_current_token()
        # output "call f n" or "call f n+1"
        self.vm_writer.write_call(function_call_name, n + is_method)

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # keyword = do
        self.__get_current_token()
        # varName or className
        name = self.__get_current_token_and_advance()
        # . -> ?
        self.__get_current_token_and_advance()
        # subroutine call
        self.__subroutine_call_format(name, False)
        # ;
        self.__get_current_token_and_advance()
        self.vm_writer.write_pop("TEMP", 0)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # keyword = let
        self.__get_current_token()
        # identifier
        var_name = self.__get_current_token_and_advance()
        var_type, var_kind, var_index = self.__get_var_info_from_table(var_name)
        # [ -> ?
        symbol = self.__get_current_token_and_advance()
        # handle array
        is_array = False
        if symbol == "[":
            # push x
            self.vm_writer.write_push(var_kind, var_index)
            # expression
            self.__get_current_token_and_advance()
            self.compile_expression()
            # ]
            self.__get_current_token_and_advance()
            # add
            self.vm_writer.write_arithmetic("ADD")
            is_array = True
        # symbol
        self.__get_current_token()
        # expression
        self.__get_current_token_and_advance()
        self.compile_expression()
        # ;
        self.__get_current_token()
        if is_array:
            # pop temp 0
            self.vm_writer.write_pop("TEMP", 0)
            # pop pointer 1
            self.vm_writer.write_pop("POINTER", 1)
            # push temp 0
            self.vm_writer.write_push("TEMP", 0)
            # pop that 0
            self.vm_writer.write_pop("THAT", 0)
        else:
            self.vm_writer.write_pop(var_kind, var_index)

    def compile_while(self, subroutine_type: str) -> None:
        """Compiles a while statement."""
        # keyword = while
        self.__get_current_token()
        # label L1
        l1 = f"""{self.class_name}_L_{self.counter}"""
        self.counter += 1
        self.vm_writer.write_label(l1)
        # (
        self.__get_current_token_and_advance()
        # expression
        self.__get_current_token_and_advance()
        self.compile_expression()
        # )
        self.__get_current_token()
        # not
        self.vm_writer.write_arithmetic("NOT")
        # if-goto L2
        l2 = f"""{self.class_name}_L_{self.counter}"""
        self.counter += 1
        self.vm_writer.write_if(l2)
        # {
        # statements
        self.__get_current_token_and_advance()
        self.compile_statements(subroutine_type)
        # }
        self.__get_current_token()
        # goto L1
        self.vm_writer.write_goto(l1)
        # label L2
        self.vm_writer.write_label(l2)

    def compile_return(self, subroutine_type: str) -> None:
        """Compiles a return statement."""
        # keyword = return
        self.__get_current_token()
        # expression -> ?
        symbol = self.__get_current_token_and_advance()
        if symbol != ";":
            # expression
            self.compile_expression()
        else:
            if subroutine_type == self.CONSTRUCTOR:
                self.vm_writer.write_push("POINTER", 0)
            else:
                self.vm_writer.write_push("CONST", 0)
        self.vm_writer.write_return()

    def compile_if(self, subroutine_type: str) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # keyword = if
        self.__get_current_token()
        # (
        self.__get_current_token_and_advance()
        # expression
        self.__get_current_token_and_advance()
        self.compile_expression()
        # )
        self.__get_current_token()
        # not
        self.vm_writer.write_arithmetic("NOT")
        # if-goto L1
        l1 = f"""{self.class_name}_L_{self.counter}"""
        self.counter += 1
        self.vm_writer.write_if(l1)
        # {
        self.__get_current_token_and_advance()
        # statements
        self.__get_current_token_and_advance()
        self.compile_statements(subroutine_type)
        # }
        self.__get_current_token()
        # goto L2
        l2 = f"""{self.class_name}_L_{self.counter}"""
        self.counter += 1
        self.vm_writer.write_goto(l2)
        # label L1
        self.vm_writer.write_label(l1)
        # else -> ?
        token = self.__get_current_token_and_advance()
        if token == self.ELSE:
            # {
            self.__get_current_token_and_advance()
            # statements
            self.__get_current_token_and_advance()
            self.compile_statements(subroutine_type)
            # }
            self.__get_current_token()
            self.__get_current_token_and_advance()
        # label L2
        self.vm_writer.write_label(l2)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # term
        self.compile_term()
        # term -> *
        token = self.__get_current_token()
        while token != ")":
            if token not in self.op_terms:
                break
            # op
            op = token
            # term
            self.__get_current_token_and_advance()
            # term
            self.compile_term()
            # output "op"
            self.vm_writer.write_arithmetic(self.op_terms[op])
            token = self.__get_current_token()

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # identifier / symbol
        token = self.__get_current_token()
        # push const
        if token.isnumeric():
            self.vm_writer.write_push("CONST", int(token))
        elif token == "true":
            self.vm_writer.write_push("CONST", 1)
            self.vm_writer.write_arithmetic("NEG")
        elif token == "false":
            self.vm_writer.write_push("CONST", 0)
        elif token == "null":
            self.vm_writer.write_push("CONST", 0)
        elif token == "this":
            self.vm_writer.write_push("POINTER", 0)
        elif self.tokenizer.token_type() == "STRING_CONST":
            self.__compile_string(token)
        # push var
        elif self.class_symbol_table.kind_of(token) is not None or \
                self.subroutine_symbol_table.kind_of(token) is not None:
            var_type, var_kind, var_index = self.__get_var_info_from_table(token)
            self.vm_writer.write_push(var_kind, var_index)
        # unary term -> ?
        if token in self.unary_op_terms:
            self.__get_current_token_and_advance()
            # term
            self.compile_term()
            # output unaryOp
            self.vm_writer.write_arithmetic(self.unary_op_terms[token])
        # expression - > ?
        elif token == "(":
            # expression
            self.__get_current_token_and_advance()
            self.compile_expression()
            # )
            # self.__get_current_token()
            self.__get_current_token_and_advance()
        else:
            function_call_name = token
            token = self.__get_current_token_and_advance()
            # handle array
            # [ -> ?
            if token == "[":
                # expression
                self.__get_current_token_and_advance()
                self.compile_expression()
                # ]
                # self.__get_current_token()
                self.__get_current_token_and_advance()
                # add
                self.vm_writer.write_arithmetic("ADD")
                # pop pointer 1
                self.vm_writer.write_pop("POINTER", 1)
                # push that 0
                self.vm_writer.write_push("THAT", 0)
            # subroutine call -> ?
            elif token in {".", "("}:
                self.__subroutine_call_format(function_call_name, True)
                self.__get_current_token_and_advance()

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        n = 0
        # expression -> ?
        token = self.__get_current_token()
        while token != ")":
            # expression
            self.compile_expression()
            n += 1
            token = self.__get_current_token()
            if token == ",":
                token = self.__get_current_token_and_advance()
        return n
