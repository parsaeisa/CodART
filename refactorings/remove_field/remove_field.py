import os
import time

from antlr4 import *
from antlr4.TokenStreamRewriter import TokenStreamRewriter as TSR

from gen.javaLabeled.JavaParserLabeled import *
from gen.javaLabeled.JavaParserLabeledListener import *


class RemoveFieldRefactoringListener(JavaParserLabeledListener):
    def __init__(self, common_token_stream: CommonTokenStream = None, class_identifier: str = None,
                 fieldname: str = None, filename: str = None):
        """
        :param common_token_stream:
        """
        self.enter_class = False
        self.enter_field = False
        self.is_found_field = False
        self.is_found = False
        self.token_stream = common_token_stream
        self.class_identifier = class_identifier
        self.class_number = 0

        # Move all the tokens in the source code in a buffer, token_stream_rewriter.
        if common_token_stream is not None:
            self.token_stream_rewriter = TSR(common_token_stream)
        else:
            raise TypeError('common_token_stream is None')

        self.class_fields = []
        self.class_methods = []

        if class_identifier is not None:
            self.class_identifier = class_identifier
        else:
            raise ValueError("class_identifier is None")

        if filename is not None:
            self.filename = filename
        else:
            raise ValueError("filename is None")

        if fieldname is not None:
            self.fieldname = fieldname
        else:
            raise ValueError("fieldname is None")

    def enterClassDeclaration(self, ctx:JavaParserLabeled.ClassDeclarationContext):
        print("Refactoring started, please wait...")
        self.class_number += 1
        if ctx.IDENTIFIER().getText() != self.class_identifier:
            return
        self.enter_class = True

    # Enter a parse tree produced by Java9_v2Parser#normalClassDeclaration.
    # def enterNormalClassDeclaration(self, ctx: Java9_v2Parser.NormalClassDeclarationContext):
    #     print("Refactoring started, please wait...")
    #     self.class_number += 1
    #     if ctx.identifier().getText() != self.class_identifier:
    #         return
    #     self.enter_class = True

    def exitClassDeclaration(self, ctx:JavaParserLabeled.ClassDeclarationContext):
        self.enter_class = False
        if ctx.IDENTIFIER().getText() != self.class_identifier:
            return

        old_file = open(self.filename, 'w')
        old_file.write(self.token_stream_rewriter.getDefaultText().replace("\r", ""))

    # Exit a parse tree produced by Java9_v2Parser#normalClassDeclaration.
    # def exitNormalClassDeclaration(self, ctx: Java9_v2Parser.NormalClassDeclarationContext):
    #     self.enter_class = False
    #     if ctx.identifier().getText() != self.class_identifier:
    #         return
    #
    #     old_file = open(self.filename, 'w')
    #     old_file.write(self.token_stream_rewriter.getDefaultText().replace("\r", ""))
    #
    #     # print("----------------------------")
    #     # print("Class attributes: ", str(self.class_fields))
    #     # print("Class methods: ", str(self.class_methods))
    #     # print("----------------------------")

    # Enter a parse tree produced by Java9_v2Parser#fieldDeclaration.

    def enterFieldDeclaration(self, ctx:JavaParserLabeled.FieldDeclarationContext):
        if not self.enter_class:
            return
        self.enter_field = True
        self.is_found_field = False

    # def enterFieldDeclaration(self, ctx:Java9_v2Parser.FieldDeclarationContext):
    #     if not self.enter_class:
    #         return
    #     self.enter_field = True
    #     self.is_found_field = False

    # Exit a parse tree produced by Java9_v2Parser#fieldDeclaration.

    def exitClassBodyDeclaration2(self, ctx:JavaParserLabeled.ClassBodyDeclaration2Context):
        if not self.enter_class:
            return

        # print("Enter 'exitFieldDeclaration' Methode")
        start = ctx.start.tokenIndex
        stop = ctx.stop.tokenIndex

        if (self.is_found_field):
            self.token_stream_rewriter.delete(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                              from_idx=start,
                                              to_idx=stop)
            print(f'Field: "{self.fieldname}" SUCCESSFULLY REMOVED...')

    # def exitFieldDeclaration(self, ctx:JavaParserLabeled.FieldDeclarationContext):
    #     if not self.enter_class:
    #         return
    #
    #     # print("Enter 'exitFieldDeclaration' Methode")
    #     start = ctx.start.tokenIndex
    #     stop = ctx.stop.tokenIndex
    #
    #     if (self.is_found_field):
    #         self.token_stream_rewriter.delete(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
    #                                           from_idx=start,
    #                                           to_idx=stop)
    #         print(f'Field: "{self.fieldname}" SUCCESSFULLY REMOVED...')

    # def exitFieldDeclaration(self, ctx: Java9_v2Parser.FieldDeclarationContext):
    #     if not self.enter_class:
    #         return
    #
    #     # print("Enter 'exitFieldDeclaration' Methode")
    #     start = ctx.start.tokenIndex
    #     stop = ctx.stop.tokenIndex
    #
    #     if (self.is_found_field):
    #         self.token_stream_rewriter.delete(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
    #                                           from_idx=start,
    #                                           to_idx=stop)
    #         print(f'Field: "{self.fieldname}" SUCCESSFULLY REMOVED...')

    # Exit a parse tree produced by Java9_v2Parser#variableDeclaratorList.

    def exitVariableDeclarators(self, ctx:JavaParserLabeled.VariableDeclaratorsContext):
        if not (self.enter_class and self.enter_field):
            return
        # print("Enter 'exitVariableDeclaratorList' Methode")
        fields = ctx.getText().split(',')
        start = ctx.start.tokenIndex
        stop = ctx.stop.tokenIndex
        for index, field in enumerate(fields):
            if (self.fieldname == str(field).split('=')[0]):
                self.is_found = True
                self.is_found_field = True
                print(f'Find "{self.fieldname}", At: {start} - {stop}')
                if (len(fields) == 1):
                    return
                del fields[index]
                print('New: ' ,', '.join(str(field) for field in fields))
                self.token_stream_rewriter.replace(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
                                                   from_idx=start,
                                                   to_idx=stop,
                                                   text=', '.join(str(field) for field in fields))
                self.is_found_field = False
                print(f'Field: "{self.fieldname}" SUCCESSFULLY REMOVED...')
                break

    # def exitVariableDeclaratorList(self, ctx:Java9_v2Parser.VariableDeclaratorListContext):
    #     if not (self.enter_class and self.enter_field):
    #         return
    #     # print("Enter 'exitVariableDeclaratorList' Methode")
    #     fields = ctx.getText().split(',')
    #     start = ctx.start.tokenIndex
    #     stop = ctx.stop.tokenIndex
    #     for index, field in enumerate(fields):
    #         if (self.fieldname == str(field).split('=')[0]):
    #             self.is_found = True
    #             self.is_found_field = True
    #             print(f'Find "{self.fieldname}", At: {start} - {stop}')
    #             if (len(fields) == 1):
    #                 return
    #             del fields[index]
    #             print('New: ' ,', '.join(str(field) for field in fields))
    #             self.token_stream_rewriter.replace(program_name=self.token_stream_rewriter.DEFAULT_PROGRAM_NAME,
    #                                                from_idx=start,
    #                                                to_idx=stop,
    #                                                text=', '.join(str(field) for field in fields))
    #             self.is_found_field = False
    #             print(f'Field: "{self.fieldname}" SUCCESSFULLY REMOVED...')
    #             break

    def exitCompilationUnit(self, ctx:JavaParserLabeled.CompilationUnitContext):
        if not self.is_found:
            print(f'Field "{self.fieldname}" NOT FOUND...')

    # # Exit a parse tree produced by Java9_v2Parser#ordinaryCompilation.
    # def exitOrdinaryCompilation(self, ctx:Java9_v2Parser.OrdinaryCompilationContext):
    #     if not self.is_found:
    #         print(f'Field "{self.fieldname}" NOT FOUND...')
    #
    # # Exit a parse tree produced by Java9_v2Parser#modularCompilation.
    # def exitModularCompilation(self, ctx:Java9_v2Parser.ModularCompilationContext):
    #     if not self.is_found:
    #         print(f'Field "{self.fieldname}" NOT FOUND...')
