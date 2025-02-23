import sys

### ============= Helper Functions =============
def categorize(char):
    if char.isalpha() or char == '_':
        return "alpha"
    elif char.isnumeric():
        return "digit"
    elif char == '+' or char == '-':
        return "addOp"
    elif char == '*' or char == '/':
        return "mulOp"
    elif char == '<' or char == '>':
        return "relOp"
    elif char == ':':
        return "asgn"
    elif char == "=":
        return "equal"
    elif char == ';' or char == ',':
        return "delimiter"
    elif char == '(' or char == ')' or char == '[' or char == ']':
        return "group"
    elif char == '{':
        return "comment"
    elif char == '%':
        return "pointer"
    elif char == ' ' or char == '\t':
        return "whitespace"
    elif char == '':
        return "EOF"
    else:
        return "character error"
    
### ============================================

### ============= Global Definitions =============
source_file = sys.argv[1]

line_number = 0

state = "start"

keywords = [
    "πρόγραμμα",    "δήλωση",       "εάν",
    "τότε",         "αλλιώς",       "εάν_τέλος",
    "επανέλαβε",    "μέχρι",        "όσο",
    "όσο_τέλος",    "για",          "έως",
    "με_βήμα",      "για_τέλος",    "διάβασε",
    "γράψε",        "συνάρτηση",    "διαδικασία",
    "διαπροσωπεία", "είσοδος",      "έξοδος",
    "ή",            "και",          "εκτέλεσε",
    "όχι",
    "αρχή_συνάρτησης",              "τέλος_συνάρτησης",
    "αρχή_διαδικασίας",             "τέλος_διαδικασίας",
    "αρχή_προγράμματος",            "τέλος_προγράμματος"
]

""" Token class:

Contains info about the derived token from the source code,
such as:
- the token itself
- the family it belongs to
and
- the line number it was found
"""
class Token:
    def __init__(self, recognized_string, family, line_number):
        self.recognized_string = recognized_string
        self.family = family
        self.line_number = line_number

    def __str__(self):
        return self.recognized_string + "\t family: " + self.family + "\t line: " + str(self.line_number + 1)

### ==============================================

### ============= Lexer =============
class Lexer:
    program_lines = []
    line_index = 0

    def __init__(self, file_path):
        global line_number
        self.file_path = file_path

        if not(file_path.endswith(".gpp")):
            print("Filetype Error: Not a .gpp file")
            exit()
        
        fd = open(file_path, "r", encoding="utf-8")
        self.program_lines = [line.rstrip() for line in fd]
        # DEBUG
        # print(self.program_lines)
        fd.close()

    def error(self, case):
        print("Lexer error in line: " + str(line_number))

        if case == "number":
            print("\tIllegal number constant. Can not contain non-numerical values")
        elif case == "numberRange":
            print("\tIllegal number constant. Out of range (-32767 to 32767)")
        elif case == "limits":
            print("\tIllegal length of variable name. Must be between 1 and 30 characters")
        elif case == "EOF":
            print("\tEOF reached. Comments are opened but never closed")
        elif case == "unknown":
            print("\tUnknown character error")
        elif case == "assign":
            print("\t'=' expected")
        
        exit()
        
    def nextToken(self):
        global line_number
        current_line = ""
        current_string = ""
        family = ""

        var_name_len = 30

        line_length = len(self.program_lines[line_number])
        while (line_length == 0 or self.line_index >= line_length):
            line_number += 1
            self.line_index = 0
            
            if line_number >= len(self.program_lines):
                exit()

            line_length = len(self.program_lines[line_number])

        current_line = [line.rstrip() for line in self.program_lines[line_number]]

        while(True):
            char = current_line[self.line_index]
            category = categorize(char)

            if char == '':
                self.line_index += 1
            
            elif category == "alpha":
                while category == "alpha" or category == "digit":
                    current_string += char

                    var_name_len -= 1
                    self.line_index += 1

                    if var_name_len < 0:
                        self.error("limits")
                    if self.line_index >= len(current_line):
                        break

                    char = current_line[self.line_index]
                    category = categorize(char)

                if current_string in keywords:
                    family = "keyword"
                    break
                else:
                    family = "id"
                    break

            elif category == "digit":
                while category == "digit":
                    current_string += char
                    self.line_index += 1

                    if category == "alpha":
                        self.error("number")
                    if self.line_index >= len(current_line):
                        break

                    char = current_line[self.line_index]
                    category = categorize(char)

                if int(current_string) < -32767 or int(current_string) > 32767:
                    self.error("numberRange")

                family = "number"
                break

            elif category == "delimiter":
                current_string += char
                self.line_index += 1

                family = "delimiter"
                break

            elif category == "addOp":
                current_string += char
                self.line_index += 1
                
                family = "addOperator"
                break
            
            elif category == "mulOp":
                current_string += char
                self.line_index += 1
                
                family = "mulOperator"
                break

            elif category == "relOp":
                current_string += char
                self.line_index += 1
                
                char = current_line[self.line_index]
                category = categorize(char)

                if category == "equal":
                    current_string += char
                    
                family = "relationalOperator"
                break

            elif category == "asgn":
                current_string += char
                self.line_index += 1

                char = current_line[self.line_index]
                category = categorize(char)

                if category == "equal":
                    current_string += char
                    family = "assignOperator"
                    break
                else:
                    self.error("assign")
            
            elif category == "group":
                current_string += char
                self.line_index += 1

                family = "group"
                break

            elif category == "comment":
                com_open_line = line_number + 1
                com_open = True

                while char != "}" and line_number < len(self.program_lines)-1:
                    self.line_index += 1
                    if self.line_index >= len(current_line):
                        line_number += 1
                        self.line_index = 0

                        current_line = [line.rstrip() for line in self.program_lines[line_number]]

                    char = current_line[self.line_index]

                    if char == '}':
                        com_open = False
                        break
                
                if com_open:
                    line_number = com_open_line
                    self.error("EOF")
                else:
                    self.line_index += 1

                    family = "comment"
                    break

            elif category == "pointer":
                current_string += char
                self.line_index += 1

                family = "pointer"
                break

            elif category == "EOF":
                current_string = "EOF"
                family = "EOF"
                break

            elif category == "character error":
                self.error("unknown")
            else:
                self.error("unknown")

        next_token = Token(current_string, family, line_number)

        #TODO: Remove this
        # DEBUG
        print(next_token)
        
        return next_token
    
### =================================

### ============= Parser =============
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

    def error(self, case):
        print("Parser error in line: " + str(token.line_number + 1))

        if case == "program":
            print("\t'πρόγραμμα' expected")
        elif case == "name":
            print("\tProgram name expected")
        elif case == "start":
            print("\t'αρχή_προγράμματος' expected")
        elif case == "end":
            print("\t'τελός_προγράμματος' expected")
        elif case == "varDec":
            print("\tVariable name expected")
        elif case == "statement":
            print("\tStatement expected")
        elif case == "assign":
            print("\tAssignment operator ':=' expected after variable name")
        elif case == "if-then":
            print("\t'τότε' expected after 'εάν'")
        elif case == "if-end":
            print("\t'εάν' block is never closed")
        elif case == "while-end":
            print("\t'όσο' block is never closed")
        elif case == "do-end":
            print("\t'επανέλαβε' ending condition is not found")
        elif case == "for-end":
            print("\t'για' block is never closed")
        elif case == "for-do":
            print("\t'επανέλαβε' expected after 'για'")
        elif case == "for-range":
            print("\t'έως' expected after 'για'")
        elif case == "funDec":
            print("\tFunction name expected")
        elif case == "sqBracketsClose":
            print("\t'[' is not closed")
        elif case == "sqBracketsOpen":
            print("\t'[' expected")
        elif case == "bracketsOpen":
            print("\t'(' expected after function or procedure name")
        elif case == "bracketsClose":
            print("\t'(' is not closed")
        elif case == "optionalSign":
            print("\t'+' or '-' or expression expected")
        elif case == "relOp":
            print("\t'<', '>', '<=', '>=', '=' or '<>' operator expected")
        elif case == "parList":
            print("\tOptional parameter list expected")
        elif case == "func-end":
            print("\tFunction block is never closed")
        elif case == "func-start":
            print("\tFunction block is never opened")
        elif case == "func-interface":
            print("\t'διαπροσωπεία' expected")
        elif case == "proc-end":
            print("\tProcedure block is never closed")
        elif case == "proc-start":
            print("\tProcedure block is never opened")
        elif case == "proc-interface":
            print("\t'διαπροσωπεία' expected")
        elif case == "func-input":
            print("\tInput parameter list, or Output parameter list, or variable declarationexpected")            
        elif case == "func-output":
            print("\tOutput parameter list, or variable declarationexpected")

        exit()

    def get_token(self):
        global token
        token = self.lexer.nextToken()

        if token.family == "comment":
            token = self.lexer.nextToken()

        #TODO: dont know if this actually belongs here

        #     while token.family == "comment" and token.family != "EOF":
        #         token = self.lexer.nextToken()

            # token = self.lexer.nextToken() #get the next token after the comment one

        return token

    def syntax_analyzer(self):
        print("Syntax analyzer started")
        global token
        token = self.get_token()
        self.program()
        print("Program compiled successfully")

    def program(self):
        global token
        
        if token.recognized_string == "πρόγραμμα":
            token = self.get_token()

            if token.family == "id":
                token = self.get_token()
                self.program_block()
            else:
                self.error("name")

        else:
            self.error("program")

    def program_block(self):
        global token

        self.declarations()
        token = self.get_token()
        self.subprograms()

        if token.recognized_string == "αρχή_προγράμματος":
            token = self.get_token()

            self.sequence()
        else:
            self.error("start")

        if token.recognized_string == "τέλος_προγράμματος":
            exit()
        else:
            self.error("end")

    def declarations(self):
        global token

        if token.recognized_string == "δήλωση":
            token = self.get_token()

            self.varlist()
        
        elif token.recognized_string not in keywords:
            self.error("varDec")


    # varlist() updates the token at the end
    # so there is no need to call get_token()
    # after varlist() is called in the code
    def varlist(self):
        global token
        
        if token.family == "id":
            while token.family == "id":
                token = self.get_token()

                if token.recognized_string == ",":
                    token = self.get_token()

                    if token.family == "id":
                        token = self.get_token()
                    else:
                        self.error("varDec")

                else:
                    break
            
        else:
            self.error("varDec")

    # subprograms() updates the token at the end
    # so there is no need to call get_token()
    # after subprograms() is called in the code
    def subprograms(self):
        global token

        while token.recognized_string == "συνάρτηση" or token.recognized_string == "διαδικασία":
            if token.recognized_string == "συνάρτηση":
                token = self.get_token()

                self.func()

            elif token.recognized_string == "διαδικασία":
                token = self.get_token()

                self.proc()

            token = self.get_token()

    def func(self):
        global token

        if token.family == "id":
            token = self.get_token()

            if token.recognized_string == "(":
                token = self.get_token()

                self.formalparlist()

                if token.recognized_string == ")":
                    token = self.get_token()

                    self.funcblock()

                else:
                    self.error("bracketsClose")
            else:
                self.error("bracketsOpen")
        else:
            self.error("funDec")

    def proc(self):
        global token

        if token.family == "id":
            token = self.get_token()

            if token.recognized_string == "(":
                token = self.get_token()

                self.formalparlist()

                if token.recognized_string == ")":
                    token = self.get_token()

                    self.procblock()
                else:
                    self.error("bracketsClose")
            else:
                self.error("bracketsOpen")
        else:
            self.error("funDec")

    def formalparlist(self):
        global token

        if token.family == "id":
            self.varlist()
        elif token.recognized_string != ")":
            self.error("parList")

    def funcblock(self):
        global token

        if token.recognized_string == "διαπροσωπεία":
            token = self.get_token()

            self.funcinput()
            self.funcoutput()
            self.declarations()

            token = self.get_token()

            if token.recognized_string == "αρχή_συνάρτησης":
                token = self.get_token()

                self.sequence()

                if token.recognized_string != "τέλος_συνάρτησης":
                    self.error("func-end")
            
            else:
                self.error("func-start")
        else:
            self.error("func-interface")

    def procblock(self):
        global token

        if token.recognized_string == "διαπροσωπεία":
            token = self.get_token()

            self.funcinput()
            self.funcoutput()
            self.declarations()

            token = self.get_token()

            if token.recognized_string == "αρχή_διαδικασίας":
                token = self.get_token()

                self.sequence()

                if token.recognized_string != "τέλος_διαδικασίας":
                    self.error("proc-end")
            else:
                self.error("proc-start")
        else:
            self.error("proc-interface")

    def funcinput(self):
        global token

        if token.recognized_string == "είσοδος":
            token = self.get_token()

            if token.family == "id":
                self.varlist()
            else:
                self.error("varDec")
        
        elif token.recognized_string == "έξοδος":
            self.funcoutput()

        elif token.recognized_string == "δήλωση":
            self.declarations()
        
        else:
            self.error("func-input")

    def funcoutput(self):
        global token

        if token.recognized_string == "έξοδος":
            token = self.get_token()

            if token.family == "id":
                self.varlist()
            else:
                self.error("varDec")
        
        elif token.recognized_string == "δήλωση":
            self.declarations()
        
        else:
            self.error("func-output")

    # sequence() updates the token at the end
    # so there is no need to call get_token()
    # after sequence() is called in the code
    def sequence(self):
        global token

        self.statement()

        token = self.get_token()

        while token.recognized_string == ";":
            token = self.get_token()

            self.statement()

            token = self.get_token()
        
    def statement(self):
        global token

        if token.family == "id":
            self.assignement_stat()

        elif token.recognized_string == "εάν":
            self.if_stat()

        elif token.recognized_string == "όσο":
            self.while_stat()

        elif token.recognized_string == "επανέλαβε":
            self.do_stat()
        
        elif token.recognized_string == "για":
            self.for_stat()

        elif token.recognized_string == "διάβασε":
            self.input_stat()

        elif token.recognized_string == "γράψε":
            self.print_stat()

        elif token.recognized_string == "εκτέλεσε":
            self.call_stat()

        else:
            self.error("statement")

    def assignement_stat(self):
        global token
        token = self.get_token()

        if token.recognized_string == ":=":
            token = self.get_token()

            self.expression()
        else:
            self.error("assign")

    def if_stat(self):
        global token
        token = self.get_token()

        self.condition()

        token = self.get_token()

        if token.recognized_string == "τότε":
            token = self.get_token()

            self.sequence()
            self.elsepart()

            if token.recognized_string != "εάν_τέλος":
                self.error("if-end")
            else:
                token = self.get_token()
        else:
            self.error("if-then")

    def elsepart(self):
        global token
        token = self.get_token()

        if token.recognized_string == "αλλιώς":
            token = self.get_token()

            self.sequence()

    def while_stat(self):
        global token
        token = self.get_token()

        self.condition()

        token = self.get_token()

        if token.recognized_string == "επανέλαβε":
            token = self.get_token()

            self.sequence()

            if token.recognized_string != "οσο_τέλος":
                self.error("while-end")

    def do_stat(self):
        global token
        token = self.get_token()

        self.sequence()

        if token.recognized_string == "μέχρι":
            token = self.get_token()

            self.condition()

            token = self.get_token()

        else:
            self.error("do-end")

    def for_stat(self):
        global token
        token = self.get_token()

        if token.family == "id":
            token = self.get_token()

            if token.recognized_string == ":=":
                token = self.get_token()

                self.expression()

                token = self.get_token()

                if token.recognized_string == "έως":
                    token = self.get_token()

                    self.expression()

                    token = self.get_token()

                    self.step()

                    token = self.get_token()

                    if token.recognized_string == "επανέλαβε":
                        token = self.get_token()

                        self.sequence()

                        if token.recognized_string != "για_τέλος":
                            self.error("for-end")

                    else:
                        self.error("for-do")
                else:
                    self.error("for-range")
            else:
                self.error("assign")
        else:
            self.error("varDec")

    def step(self):
        global token

        if token.recognized_string == "με_βήμα":
            token = self.get_token()

            self.expression()

    def input_stat(self):
        global token
        token = self.get_token()

        if token.family == "id":
            token = self.get_token()
        else:
            self.error("varDec")

    def print_stat(self):
        global token
        token = self.get_token()

        self.expression()

    def call_stat(self):
        global token
        token = self.get_token()

        if token.family == "id":
            token = self.get_token()

            self.idtail()
        else:
            self.error("funDec")

    def idtail(self):
        global token

        self.actualpars()

    def actualpars(self):
        global token

        if token.recognized_string == "(":
            token = self.get_token()

            self.actualparlist()

            if token.recognized_string != ")":
                self.error("parEnd")
            

    # just like sequence(), actualparlist() updates
    # the token at the end so there is no need to 
    # call get_token() after actualparlist() is called in the code
    def actualparlist(self):
        global token

        self.actualparitem()

        token = self.get_token()

        while token.recognized_string == ",":
            token = self.get_token()

            self.actualparitem()

            token = self.get_token()

    def actualparitem(self):
        global token

        if token.recognized_string != "%":
            self.expression()
        else:
            token = self.get_token()

            if token.family != "id":
                self.error("varDec")

    # condition() updates the token at the end
    # like sequence() and actualparlist()
    def condition(self):
        global token

        self.boolterm()

        token = self.get_token()

        while token.recognized_string == "ή":
            token = self.get_token()

            self.boolterm()

            token = self.get_token()

    # boolterm() also updates the token at the end
    def boolterm(self):
        global token

        self.boolfactor()

        token = self.get_token()

        while token.recognized_string == "και":
            token = self.get_token()

            self.boolfactor()

            token = self.get_token()

    def boolfactor(self):
        global token

        if token.recognized_string == "όχι":
            token = self.get_token()

            if token.recognized_string == "[":
                token = self.get_token()

                self.condition()

                if token.recognized_string != "]":
                    self.error("sqBracketsClose")
            else:
                self.error("sqBracketsOpen")
        
        elif token.recognized_string == "[":
            token = self.get_token()

            self.condition()

            if token.recognized_string != "]":
                self.error("sqBracketsClose")

        else:
            self.expression()
            self.relational_oper()
            token = self.get_token()
            self.expression()

    # expression() also updates the token at the end
    def expression(self):
        global token

        self.optional_sign()
        self.term()

        token = self.get_token()

        while token.recognized_string == "+" or token.recognized_string == "-":
            token = self.get_token()

            self.term()

            token = self.get_token()

    def optional_sign(self):
        global token

        if token.family != "addOperator" and token.family != "number" and token.recognized_string != "(" and token.family != "id":
            self.error("optionalSign")


    # term() also updates the token at the end
    def term(self):
        global token

        self.factor()

        token = self.get_token()

        while token.recognized_string == "*" or token.recognized_string == "/":
            token = self.get_token()

            self.factor()

            token = self.get_token()

    def factor(self):
        global token

        if token.family == "number":
            pass

        elif token.recognized_string == "(":
            token = self.get_token()

            self.expression()

            if token.recognized_string != ")":
                self.error("bracketsClose")

        elif token.family == "id":
            token = self.get_token()

            self.idtail()

    def relational_oper(self):
        global token

        if token.family != "relationalOperator":
            self.error("relOp")
        
### ==================================

def main():
    lexer = Lexer(source_file)
    # lexer.nextToken()
    # lexer.nextToken()
    # lexer.nextToken()
    # lexer.nextToken()
    # lexer.nextToken()
    # lexer.nextToken()
    # lexer.nextToken()
    # lexer.nextToken()
    # lexer.nextToken()
    # lexer.nextToken()
    # lexer.nextToken()

    parser = Parser(lexer)
    parser.syntax_analyzer()

main()