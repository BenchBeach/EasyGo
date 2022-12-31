from antlr4.ListTokenSource import ListTokenSource

from parser_.gen.GoParserVisitor import GoParserVisitor
from parser_.gen.GoLexer import GoLexer
from parser_.gen.GoParser import GoParser
from antlr4 import *
import llvmlite.ir as ir
from generator.types import EasyGoTypes
from generator.util import *
from generator.errors import *
from generator.symbol_table import SymbolTable, RedefinitionError


class EasyGoGenerator(GoParserVisitor):
    def __init__(self, error_listener=EasyGoErrorListener()):
        self.module = ir.Module()
        self.builder = ir.IRBuilder()
        self.symbol_table = SymbolTable()  # 符号表
        self.continue_block = None  # 当调用continue时应该跳转到的语句块
        self.break_block = None  # 当调用break时应该跳转到的语句块
        self.switch_context = None  # TODO
        self.current_base_type = None  # 当前上下文的基础数据类型
        self.is_global = True  # 当前是否处于全局环境中
        self.error_listener = error_listener  # 错误监听器
        self.global_context = ir.global_context
        self.struct_reflection = {}
        self.is_defining_struct = ''

    BASE_TYPE = 0
    ARRAY_TYPE = 1
    FUNCTION_TYPE = 2

    def visitDeclaration(self, ctx: GoParser.DeclarationContext):
        """
                declaration: constDecl | typeDecl | varDecl;
                :param ctx:
                :return:
                """
        return self.visit(ctx.children[0])
        pass

    def visitVarDecl(self, ctx: GoParser.VarDeclContext):
        """
                varDecl: VAR (varSpec | L_PAREN (varSpec eos)* R_PAREN);
        """
        self.visit(ctx.varSpec(0))

    def visitVarSpec(self, ctx: GoParser.VarSpecContext):
        """
        varSpec:
            identifierList (
            type_ (ASSIGN expressionList)?
            | ASSIGN expressionList
            );
        """
        idn_list = self.visit(ctx.identifierList())
        type = self.visit(ctx.type_())
        for var_name in idn_list:
            try:
                if self.is_global:  # 如果是全局变量
                    self.symbol_table[var_name] = ir.GlobalVariable(self.module, type, name=var_name)
                    self.symbol_table[var_name].linkage = "internal"
                else:  # 如果是局部变量
                    self.symbol_table[var_name] = self.builder.alloca(type)
            except RedefinitionError as e:
                raise SemanticError(msg="redefinition variable {}".format(var_name), ctx=ctx)


    def visitIdentifierList(self, ctx: GoParser.IdentifierListContext):
        idn_list = list(map(lambda x: x.getText(), ctx.IDENTIFIER()))
        return idn_list

    def visitType_(self, ctx: GoParser.Type_Context):

        """
         type_: typeName | typeLit | L_PAREN type_ R_PAREN;
        """
        if len(ctx.children) == 3:
            # handle 3rd situation
            type = self.visit(ctx.type_())
        else:
            # handle the first one
            type = self.visit(ctx.typeName())

        if type in EasyGoTypes.str2type.keys():
            return EasyGoTypes.str2type[type]
        else:
            raise NotImplementedError("visitType_")

    def visitTypeName(self, ctx: GoParser.TypeNameContext):
        return str(ctx.children[0])

    def save(self, filename):
        """保存到文件"""
        with open(filename, "w") as f:
            f.write(repr(self.module))


def generate(input_filename, output_filename):
    """
    将Go代码文件转成IR代码文件
    :param input_filename: C代码文件
    :param output_filename: IR代码文件
    :return: 生成是否成功
    """
    lexer = GoLexer(FileStream(input_filename))
    tokensStream = CommonTokenStream(lexer)
    # parser = GoParser(stream)

    # tokens = lexer.getAllTokens()
    parser = GoParser(tokensStream)

    error_listener = EasyGoErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    tree = parser.sourceFile()
    print(tree.toStringTree(recog=parser))

    generator = EasyGoGenerator(error_listener)
    generator.visit(tree)
    generator.save(output_filename)

    if len(error_listener.errors) == 0:
        return True
    else:
        error_listener.print_errors()
        return False
