import os
import re
import sys
import Token

SYMBOLS = {"{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-",
           "/", "&", "|", "<", ">", "=", "~", "*"}
KEYWORDS = {"class", "constructor", "function", "method", "field",
            "static", "var", "int", "char", "boolean",
            "void", "true", "false", "null",
            "this", "let", "do", "if", "else", "while", "return"}
IDENTIFIER_REGEX = "\\w"
COMMENT_REGEX = "//|/\\*"

TYPE_KEYWORD = "keyword"
TYPE_STRING = "stringConstant"
TYPE_INTEGER = "integerConstant"
TYPE_SYMBOL = "symbol"
TYPE_IDENTIFIER = "identifier"


class Tokenizer:

    def __init__(self, filepath):

        self.__workFile = open(filepath, "r")
        self.__head = Token.Token("", "")
        self.__currentToken = self.__head
        self.__save_token = None            # remember one token forward
        self.read()
        self.__currentToken = self.__head

    def close(self):
        """
        close workFile
        :return:
        """
        if self.__workFile:
            if not self.__workFile.closed:
                self.__workFile.close()

    def read(self):
        """
        parse the entire file and convert it into a list of tokens in the
         order of their appearance
        :return:
        """
        char = " "
        found_fore_slash = False
        while char != "":
            inline_comment = False
            multiline_comment = False
            found_string = False
            found_asterisk = False
            record_token = ""

            if self.__save_token is not None:
                self.__currentToken.set_next(self.__save_token)
                self.__currentToken = self.__currentToken.get_next()
                self.__save_token = None
                continue

            char = self.__workFile.read(1)
            while 1:
                if inline_comment:
                    if char == '\n':
                        inline_comment = False
                        found_fore_slash = False

                elif multiline_comment:
                    if char == "/" and found_asterisk:
                        multiline_comment = False
                        found_asterisk = False
                        found_fore_slash = False

                    elif char == "*":
                        found_asterisk = True
                        found_fore_slash = False
                    else:
                        found_asterisk = False
                    char = self.__workFile.read(1)
                    continue

                elif found_fore_slash and char != "/" and char != "*" \
                        and not inline_comment and not multiline_comment:
                    found_fore_slash = False
                    self.__currentToken.set_next(Token.Token(TYPE_SYMBOL, "/"))
                    self.__currentToken = self.__currentToken.get_next()
                    if not re.match("\\s", char):
                        record_token += char

                elif found_fore_slash and char == "*":
                    multiline_comment = True
                    found_fore_slash = False
                    char = self.__workFile.read(1)
                    continue

                elif char == "/":
                    if found_fore_slash:
                        inline_comment = True
                        found_fore_slash = False
                    else:
                        found_fore_slash = True
                        if record_token in KEYWORDS:
                            break
                        elif record_token.isnumeric():
                            break
                        elif re.match(IDENTIFIER_REGEX,
                                      record_token):
                            break

                elif char == "\"":
                    found_string = True
                    char = self.__workFile.read(1)
                    while char != "\"":
                        record_token += char
                        char = self.__workFile.read(1)
                    char = self.__workFile.read(1)
                    continue

                elif re.match("\\s", char):
                    if record_token in KEYWORDS or \
                            record_token.isnumeric() or \
                            re.match(IDENTIFIER_REGEX, record_token):
                        break

                elif char in SYMBOLS:
                    if found_string:
                        self.__save_token = Token.Token(TYPE_SYMBOL, char)

                    elif record_token in KEYWORDS:
                        self.__save_token = Token.Token(TYPE_SYMBOL, char)

                    elif record_token.isnumeric():
                        self.__save_token = Token.Token(TYPE_SYMBOL, char)

                    elif re.match(IDENTIFIER_REGEX, record_token):
                        self.__save_token = Token.Token(TYPE_SYMBOL, char)

                    elif record_token in SYMBOLS:
                        self.__save_token = Token.Token(TYPE_SYMBOL, char)

                    elif re.match("\\s", record_token):
                        self.__save_token = Token.Token(TYPE_SYMBOL, char)
                        break

                    else:
                        record_token += char
                    break

                else:
                    record_token += char

                char = self.__workFile.read(1)
                if char == "":
                    break
            if char == "" and record_token == "":
                break
            current_token_type = ""
            if found_string:
                current_token_type = TYPE_STRING
            elif record_token in KEYWORDS:
                current_token_type = TYPE_KEYWORD
            elif record_token in SYMBOLS:
                current_token_type = TYPE_SYMBOL
            elif record_token.isnumeric():
                current_token_type = TYPE_INTEGER
            elif re.match(IDENTIFIER_REGEX, record_token):
                current_token_type = TYPE_IDENTIFIER

            self.__currentToken.set_next(Token.Token(current_token_type,
                                                     record_token))
            self.__currentToken = self.__currentToken.get_next()

    def hasMoreTokens(self):
        """
        :return: true if there is another token
        """
        return self.__currentToken.get_next() is not None

    def advance(self):
        """
        set the current token to point at the next token
        :return:
        """
        if self.__currentToken is self.__head:
            self.__currentToken = self.__head.get_next()
            return
        self.__currentToken = self.__currentToken.get_next()
        return

    def tokenType(self):
        """
        return current token type
        :return:
        """
        if self.__currentToken is not None:
            return self.__currentToken.tokenType
        else:
            return None

    def keyWord(self):
        """
        return the keyword held by current token
        must check that type is indeed keyword before calling this method
        :return:
        """
        return self.__currentToken.get_value()

    def symbol(self):
        """
        return the symbol held by current token
        must check that type is indeed symbol before calling this method
        :return:
        """
        return self.__currentToken.get_value()

    def identifier(self):
        """
        return the identifier held by current token
        must check that type is indeed identifier before calling this method
        :return:
        """
        return self.__currentToken.get_value()

    def intVal(self):
        """
        return the integer value held by current token
        must check that type is indeed integer before calling this method
        :return:
        """
        return int(self.__currentToken.get_value())

    def stringVal(self):
        """
        return the string value held by current token
        must check that type is string integer before calling this method
        :return:
        """
        return self.__currentToken.get_value()
