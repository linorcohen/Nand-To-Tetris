"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import JackTokenizer


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

    CLASS_TAG = "class"
    CLASS_VAR_DEC_TAG = "classVarDec"
    SUBROUTINE_DEC_TAG = "subroutineDec"
    SUBROUTINE_BODY_TAG = "subroutineBody"
    VAR_DEC_TAG = "varDec"
    PARAMETER_LIST_TAG = "parameterList"
    STATEMENTS_TAG = "statements"
    EXPRESSION_LIST_TAG = "expressionList"
    TERM_TAG = "term"
    EXPRESSION_TAG = "expression"
    IF_STATEMENT_TAG = "ifStatement"
    RETURN_STATEMENT_TAG = "returnStatement"
    WHILE_STATEMENT_TAG = "whileStatement"
    LET_STATEMENT_TAG = "letStatement"
    DO_STATEMENT_TAG = "doStatement"

    KEYWORD_TAG = "keyword"
    SYMBOL_TAG = "symbol"
    IDENTIFIER_TAG = "identifier"
    INT_CONST_TAG = "integerConstant"
    STRING_CONST_TAG = "stringConstant"

    def __init__(self, input_stream: JackTokenizer, output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.output_stream = output_stream

        self.op_terms = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
        self.unary_op_terms = {"^", "#", "-", "~"}

        self.indentation = ""

    def __write_open_tag(self, tag: str) -> None:
        """
        this method writes the open tag to the output file
        :param tag: given token tag
        """
        self.output_stream.write(self.indentation + "<" + tag + ">")

    def __write_close_tag(self, tag: str) -> None:
        """
        this method writes the closing tag to the output file
        :param tag: given token tag
        """
        self.output_stream.write(self.indentation + "</" + tag + ">")
        self.output_stream.write("\n")

    def __write_open_and_close_tag(self, tag: str, token: str) -> None:
        """
        this method writes open and close tag to the output file, used for inline tags
        :param tag: given token tag
        :param token: given token
        """
        self.__write_open_tag(tag)
        if token == "<":
            token = "&lt;"
        elif token == ">":
            token = "&gt;"
        elif token == "&":
            token = "&amp;"
        self.output_stream.write(" " + token)
        self.output_stream.write(" </" + tag + ">")
        self.output_stream.write("\n")

    def __advance_tokenizer(self) -> None:
        """
        this method advance the tokenizer if has more tokens
        """
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

    def __get_current_token_and_advance(self) -> typing.Tuple[str, str]:
        """
        this method advance the token and get the current token
        :return: Tuple(token, token tag type)
        """
        self.__advance_tokenizer()
        return self.__get_current_token()

    def __get_current_token(self) -> typing.Tuple[str, str]:
        """
        this method return the tuple of the current token and the current token type tag.
        :return: Tuple(token, token tag type)
        """
        t_type = self.tokenizer.token_type()
        if t_type == self.KEYWORD:
            return self.tokenizer.keyword(), self.KEYWORD_TAG
        elif t_type == self.SYMBOL:
            return self.tokenizer.symbol(), self.SYMBOL_TAG
        elif t_type == self.IDENTIFIER:
            return self.tokenizer.identifier(), self.IDENTIFIER_TAG
        elif t_type == self.INT_CONST:
            return str(self.tokenizer.int_val()), self.INT_CONST_TAG
        elif t_type == self.STRING_CONST:
            return self.tokenizer.string_val(), self.STRING_CONST_TAG

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.__write_open_tag(self.CLASS_TAG)
        self.output_stream.write("\n")
        self.indentation += "  "
        # class
        self.__write_next_advanced_token()
        # className
        self.__write_next_advanced_token()
        # {
        self.__write_next_advanced_token()
        # classVarDec -> *
        token, token_type = self.__get_current_token_and_advance()
        while token in {self.FIELD, self.STATIC}:
            self.compile_class_var_dec()
            token, token_type = self.__get_current_token_and_advance()
        # subroutineDec -> *
        while token in {self.METHOD, self.CONSTRUCTOR, self.FUNCTION}:
            self.compile_subroutine()
            token, token_type = self.__get_current_token_and_advance()
        # }
        self.__write_open_and_close_tag(token_type, token)
        self.indentation = self.indentation[:-2]
        self.__write_close_tag(self.CLASS_TAG)

    def __write_next_advanced_token(self) -> None:
        """
        this method advance the token and writs the open close tag of the current token
        """
        token, token_type = self.__get_current_token_and_advance()
        self.__write_open_and_close_tag(token_type, token)

    def __writes_current_token(self) -> None:
        """
        this method writes the current token without advancing the tokenizer
        """
        token, token_type = self.__get_current_token()
        self.__write_open_and_close_tag(token_type, token)

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.__write_open_tag(self.CLASS_VAR_DEC_TAG)
        self.indentation += "  "
        self.output_stream.write("\n")
        # field or static
        self.__writes_current_token()
        # type
        token, token_type = self.__get_current_token_and_advance()
        self.__write_open_and_close_tag(token_type, token)
        # varName -> *
        while token != ";":
            # identifier
            self.__write_next_advanced_token()
            # symbol
            token, token_type = self.__get_current_token_and_advance()
            self.__write_open_and_close_tag(token_type, token)
        self.indentation = self.indentation[:-2]
        self.__write_close_tag(self.CLASS_VAR_DEC_TAG)

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.__write_open_tag(self.SUBROUTINE_DEC_TAG)
        self.indentation += "  "
        self.output_stream.write("\n")
        # keyword
        self.__writes_current_token()
        # identifier
        self.__write_next_advanced_token()
        # identifier
        self.__write_next_advanced_token()
        # (
        self.__write_next_advanced_token()
        # parameter list
        self.compile_parameter_list()
        # )
        self.__writes_current_token()
        # subroutine body
        self.__compile_subroutine_body()
        self.indentation = self.indentation[:-2]
        self.__write_close_tag(self.SUBROUTINE_DEC_TAG)

    def __compile_subroutine_body(self) -> None:
        """
        this method compile a subroutine body
        """
        self.__write_open_tag(self.SUBROUTINE_BODY_TAG)
        self.indentation += "  "
        self.output_stream.write("\n")
        # {
        self.__write_next_advanced_token()
        # var -> *
        token, token_type = self.__get_current_token_and_advance()
        while token == "var":
            self.compile_var_dec()
            token, token_type = self.__get_current_token_and_advance()
        # statements
        self.compile_statements()
        # }
        self.__writes_current_token()
        self.indentation = self.indentation[:-2]
        self.__write_close_tag(self.SUBROUTINE_BODY_TAG)

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.__write_open_tag(self.PARAMETER_LIST_TAG)
        self.indentation += "  "
        self.output_stream.write("\n")
        # varName -> *
        token, token_type = self.__get_current_token_and_advance()
        while token != ")":
            self.__write_open_and_close_tag(token_type, token)
            token, token_type = self.__get_current_token_and_advance()
        self.indentation = self.indentation[:-2]
        self.__write_close_tag(self.PARAMETER_LIST_TAG)

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.__write_open_tag(self.VAR_DEC_TAG)
        self.indentation += "  "
        self.output_stream.write("\n")
        # keyword
        self.__writes_current_token()
        # identifier
        token, token_type = self.__get_current_token_and_advance()
        self.__write_open_and_close_tag(token_type, token)
        # varName -> *
        while token != ";":
            # identifier
            self.__write_next_advanced_token()
            # symbol
            token, token_type = self.__get_current_token_and_advance()
            self.__write_open_and_close_tag(token_type, token)
        self.indentation = self.indentation[:-2]
        self.__write_close_tag(self.VAR_DEC_TAG)

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.__write_open_tag(self.STATEMENTS_TAG)
        self.indentation += "  "
        self.output_stream.write("\n")
        token, token_type = self.__get_current_token()
        while token != "}":
            if token == self.IF:
                self.compile_if()
                token, token_type = self.__get_current_token()
            else:
                if token == self.DO:
                    self.compile_do()
                elif token == self.LET:
                    self.compile_let()
                elif token == self.WHILE:
                    self.compile_while()
                elif token == self.RETURN:
                    self.compile_return()
                token, token_type = self.__get_current_token_and_advance()
        self.indentation = self.indentation[:-2]
        self.__write_close_tag(self.STATEMENTS_TAG)

    def __subroutine_call_format(self) -> None:
        """
        this method compile the subroutine call format
        """
        # . -> ?
        token, token_type = self.__get_current_token()
        if token == ".":
            # symbol
            self.__write_open_and_close_tag(token_type, token)
            # identifier
            self.__write_next_advanced_token()
            # ( -> ?
            token, token_type = self.__get_current_token_and_advance()
        # (
        self.__write_open_and_close_tag(token_type, token)
        # expression list
        self.__get_current_token_and_advance()
        self.compile_expression_list()
        # )
        self.__writes_current_token()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.__write_open_tag(self.DO_STATEMENT_TAG)
        self.indentation += "  "
        self.output_stream.write("\n")
        # keyword
        self.__writes_current_token()
        # identifier
        self.__write_next_advanced_token()
        # . -> ?
        self.__get_current_token_and_advance()
        # subroutine call
        self.__subroutine_call_format()
        # ;
        self.__write_next_advanced_token()
        self.indentation = self.indentation[:-2]
        self.__write_close_tag(self.DO_STATEMENT_TAG)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.__write_open_tag(self.LET_STATEMENT_TAG)
        self.indentation += "  "
        self.output_stream.write("\n")
        # keyword
        self.__writes_current_token()
        # identifier
        token, token_type = self.__get_current_token_and_advance()
        self.__write_open_and_close_tag(self.IDENTIFIER_TAG, token)
        # [ -> ?
        token, token_type = self.__get_current_token_and_advance()
        if token == "[":
            self.__write_open_and_close_tag(token_type, token)
            # expression
            self.__get_current_token_and_advance()
            self.compile_expression()
            # ]
            self.__writes_current_token()
            self.__get_current_token_and_advance()
        # symbol
        self.__writes_current_token()
        # expression
        self.__get_current_token_and_advance()
        self.compile_expression()
        # ;
        self.__writes_current_token()
        self.indentation = self.indentation[:-2]
        self.__write_close_tag(self.LET_STATEMENT_TAG)

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.__write_open_tag(self.WHILE_STATEMENT_TAG)
        self.indentation += "  "
        self.output_stream.write("\n")
        # keyword
        self.__writes_current_token()
        # (
        self.__write_next_advanced_token()
        # expression
        self.__get_current_token_and_advance()
        self.compile_expression()
        # )
        self.__writes_current_token()
        # {
        # statements
        self.__write_next_advanced_token()
        self.compile_statements()
        # }
        self.__writes_current_token()
        self.indentation = self.indentation[:-2]
        self.__write_close_tag(self.WHILE_STATEMENT_TAG)

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.__write_open_tag(self.RETURN_STATEMENT_TAG)
        self.indentation += "  "
        self.output_stream.write("\n")
        # keyword
        self.__writes_current_token()
        # expression -> ?
        token, token_type = self.__get_current_token_and_advance()
        if token != ";":
            # expression
            self.compile_expression()
            self.__writes_current_token()
        else:
            self.__write_open_and_close_tag(token_type, token)
        self.indentation = self.indentation[:-2]
        self.__write_close_tag(self.RETURN_STATEMENT_TAG)

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.__write_open_tag(self.IF_STATEMENT_TAG)
        self.indentation += "  "
        self.output_stream.write("\n")
        # keyword
        self.__writes_current_token()
        # (
        self.__write_next_advanced_token()
        # expression
        self.__get_current_token_and_advance()
        self.compile_expression()
        # )
        self.__writes_current_token()
        # {
        self.__write_next_advanced_token()
        # statements
        self.__get_current_token_and_advance()
        self.compile_statements()
        # }
        self.__writes_current_token()
        # else -> ?
        token, token_type = self.__get_current_token_and_advance()
        if token == self.ELSE:
            self.__write_open_and_close_tag(token_type, token)
            # {
            self.__write_next_advanced_token()
            # statements
            self.__get_current_token_and_advance()
            self.compile_statements()
            # }
            self.__writes_current_token()
            self.__get_current_token_and_advance()
        self.indentation = self.indentation[:-2]
        self.__write_close_tag(self.IF_STATEMENT_TAG)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.__write_open_tag(self.EXPRESSION_TAG)
        self.indentation += "  "
        self.output_stream.write("\n")
        # term
        self.compile_term()
        # term -> *
        token, token_type = self.__get_current_token()
        while token != ")":
            if token not in self.op_terms:
                break
            # op
            self.__write_open_and_close_tag(token_type, token)
            token, token_type = self.__get_current_token_and_advance()
            # term
            self.compile_term()
            token, token_type = self.__get_current_token()
        self.indentation = self.indentation[:-2]
        self.__write_close_tag(self.EXPRESSION_TAG)

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
        self.__write_open_tag(self.TERM_TAG)
        self.indentation += "  "
        self.output_stream.write("\n")
        # identifier / symbol
        token, token_type = self.__get_current_token()
        self.__write_open_and_close_tag(token_type, token)
        # unary term -> ?
        if token in self.unary_op_terms:
            self.__get_current_token_and_advance()
            # term
            self.compile_term()
        # expression - > ?
        elif token == "(":
            # expression
            self.__get_current_token_and_advance()
            self.compile_expression()
            # )
            self.__writes_current_token()
            self.__get_current_token_and_advance()
        else:
            token, token_type = self.__get_current_token_and_advance()
            # [ -> ?
            if token == "[":
                self.__write_open_and_close_tag(token_type, token)
                # expression
                self.__get_current_token_and_advance()
                self.compile_expression()
                # ]
                self.__writes_current_token()
                self.__get_current_token_and_advance()
            # subroutine call -> ?
            elif token in {".", "("}:
                self.__subroutine_call_format()
                self.__get_current_token_and_advance()
        self.indentation = self.indentation[:-2]
        self.__write_close_tag(self.TERM_TAG)

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.__write_open_tag(self.EXPRESSION_LIST_TAG)
        self.indentation += "  "
        self.output_stream.write("\n")
        # expression -> ?
        token, token_type = self.__get_current_token()
        while token != ")":
            # expression
            self.compile_expression()
            token, token_type = self.__get_current_token()
            if token == ",":
                self.__write_open_and_close_tag(token_type, token)
                token, token_type = self.__get_current_token_and_advance()
        self.indentation = self.indentation[:-2]
        self.__write_close_tag(self.EXPRESSION_LIST_TAG)
