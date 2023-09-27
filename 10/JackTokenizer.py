"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import re
import typing
import shlex


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    INITIAL_VAL = -1
    EMPTY_STR = ""
    EMPTY_LIST = []
    NOT_FOUND = -1
    COMMENT_TYPE_1 = "//"
    COMMENT_TYPE_2 = "/*"
    COMMENT_TYPE_2_END = "*/"
    COMMENT_TYPE_3 = "/**"

    TOKEN_SYMBOLS = {"{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=",
                     "~", "^", "#"}

    TOKEN_KEYWORDS = {"class", "constructor", "function", "method", "field", "static", "var", "int",
                      "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else",
                      "while", "return"}

    KEYWORD = "KEYWORD"
    SYMBOL = "SYMBOL"
    IDENTIFIER = "IDENTIFIER"
    INT_CONST = "INT_CONST"
    STRING_CONST = "STRING_CONST"

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.input_lines = input_stream.read().splitlines()
        self.n = self.INITIAL_VAL
        self.token_idx = self.INITIAL_VAL
        self.token_lst = self.EMPTY_LIST

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if self.token_idx + 1 == len(self.token_lst):
            self.token_idx = self.INITIAL_VAL
            comment = False
            while len(self.input_lines) - 1 != self.n:
                self.n += 1
                cur_token_line = self.input_lines[self.n].strip()
                if cur_token_line != self.EMPTY_STR:
                    if cur_token_line[0:2] == "/*" and cur_token_line[-2:0] == "*/":
                        continue
                    if cur_token_line[0:2] == "/*" or cur_token_line[0:3] == "/**":
                        comment = True
                    if comment and cur_token_line[-2:] == "*/":
                        comment = False
                        continue
                    if not comment and cur_token_line[0:2] != "//":
                        return True
            return False
        return True

    def __get_token_lst(self, line: str) -> typing.List[str]:
        token_line = line.replace('"', ' " ')
        temp_token_lst = list()
        for phrase in shlex.split(token_line, posix=False):
            if phrase[0] == '"':
                phrase = phrase[0] + phrase[2:-2] + phrase[-1]
                temp_token_lst.append(phrase)
            else:
                for word in phrase.split():
                    if word in self.TOKEN_KEYWORDS:
                        temp_token_lst.append(word)
                    else:
                        identifier = ""
                        for char in word:
                            if char not in self.TOKEN_SYMBOLS:
                                identifier += char
                            else:
                                if identifier != "":
                                    temp_token_lst.append(identifier)
                                    identifier = ""
                                temp_token_lst.append(char)
                        if identifier != "":
                            temp_token_lst.append(identifier)
        return temp_token_lst

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        if self.token_idx == self.INITIAL_VAL:
            cur_token_line = self.input_lines[self.n].strip()

            inline_comments = [i for i in range(len(cur_token_line)) if
                               cur_token_line.startswith(self.COMMENT_TYPE_1, i)]
            for i in inline_comments:
                if not self.__check_if_in_brackets(cur_token_line, i):
                    cur_token_line = cur_token_line[0:i]
                    break

            inline_comments = [i for i in range(len(cur_token_line)) if
                               cur_token_line.startswith(self.COMMENT_TYPE_2, i)]
            for i in inline_comments:
                if not self.__check_if_in_brackets(cur_token_line, i):
                    inline_comment_idx_end = cur_token_line.find(self.COMMENT_TYPE_2_END)
                    if inline_comment_idx_end != self.NOT_FOUND:
                        cur_token_line = cur_token_line[0:i] + cur_token_line[inline_comment_idx_end + 2:]
                        break

            inline_comment_idx = cur_token_line.find(self.COMMENT_TYPE_3)
            if inline_comment_idx != self.NOT_FOUND:
                cur_token_line = cur_token_line[0:inline_comment_idx]

            self.token_lst = self.__get_token_lst(cur_token_line)

        self.token_idx += 1

    def __check_if_in_brackets(self, cur_token_line: str, idx: int) -> bool:
        brackets = [m.start() for m in re.finditer('"', cur_token_line)]
        i = 0
        if len(brackets) == 0:
            return False
        while i + 2 <= len(brackets):
            if brackets[i] < idx < brackets[i + 1]:
                return True
            i += 2
        return False

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.token_lst[self.token_idx] in self.TOKEN_KEYWORDS:
            return self.KEYWORD

        if self.token_lst[self.token_idx] in self.TOKEN_SYMBOLS:
            return self.SYMBOL

        if self.token_lst[self.token_idx].isdecimal():
            return self.INT_CONST

        if self.token_lst[self.token_idx][-1] == '"' and self.token_lst[self.token_idx][0] == '"':
            return self.STRING_CONST

        return self.IDENTIFIER

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.token_lst[self.token_idx]

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        return self.token_lst[self.token_idx]

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.token_lst[self.token_idx]

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return int(self.token_lst[self.token_idx])

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        return self.token_lst[self.token_idx][1:-1]
