from timeit import default_timer as timer

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
    "επανάλαβε",    "μέχρι",        "όσο",
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

        if not(file_path.lower().endswith(".gr")):
            print("Filetype Error: Not a .gr file")
            exit()
        
        fd = open(file_path, "r", encoding="utf-8")
        self.program_lines = [line.rstrip() for line in fd]
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
            print("\tUnknown character error [" + token.recognized_string + "]")
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

                if category == "relOp" or category == "equal":
                    if current_string + char != "><" and current_string + char != ">>" and current_string + char != "<<":
                        current_string += char
                        self.line_index += 1    
                                    
                family = "relationalOperator"
                break

            elif category == "asgn":
                current_string += char
                self.line_index += 1

                char = current_line[self.line_index]
                category = categorize(char)

                if category == "equal":
                    current_string += char
                    self.line_index += 1
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
        # print(next_token)
        
        return next_token
    
### =================================

### ============= Parser =============
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.quad_list = QuadList()
        self.temp_counter = 1
        self.label_counter = 1

    def new_temp(self):
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp

    def error(self, case):
        print("Parser error in line: " + str(token.line_number + 1) + " " + case)

        if case == "program":
            print("\t'πρόγραμμα' expected")
        elif case == "name":
            print("\tProgram name expected")
        elif case == "start":
            print("\t'αρχή_προγράμματος' expected")
        elif case == "end":
            print("\t'τελός_προγράμματος' expected")
        elif case == "varDecl":
            print("\t'δήλωση' expected")
        elif case == "varName":
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
            print("\t'επανάλαβε' ending condition is not found")
        elif case == "for-end":
            print("\t'για' block is never closed")
        elif case == "for-do":
            print("\t'επανάλαβε' expected after 'για'")
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
            print("\tOutput parameter list, or variable declaration expected")
        elif case == "parEnd":
            print("\t'(' is not closed after function or procedure name")
        elif case == "operator":
            print("\tExpression or variable or constant expected after operator")

        exit()

    def get_token(self):
        global token
        token = self.lexer.nextToken()

        if token.family == "comment":
            token = self.lexer.nextToken()

        return token

    def syntax_analyzer(self):
        global token
        token = self.get_token()
        self.program()
        print("Syntax analyzer finished successfully")

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
        self.subprograms()

        if token.recognized_string == "αρχή_προγράμματος":
            token = self.get_token()

            self.sequence()
        else:
            self.error("start")

        if token.recognized_string != "τέλος_προγράμματος":
            self.error("end")

    def declarations(self):
        global token

        if token.recognized_string == "δήλωση":
            while token.recognized_string == "δήλωση":
                token = self.get_token()
            
            self.varlist()
        
        elif token.recognized_string not in keywords:
            self.error("varDecl")

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

                    if token.family != "id":
                        self.error("varName")

                else:
                    break
            
        else:
            self.error("varName")

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

            self.subprograms()

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
            self.declarations()

            self.subprograms()

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
                self.error("varName")
        
        elif token.recognized_string == "έξοδος":
            self.funcoutput()

        elif token.recognized_string == "δήλωση":
            self.declarations()

    def funcoutput(self):
        global token

        if token.recognized_string == "έξοδος":
            token = self.get_token()

            if token.family == "id":
                self.varlist()
            else:
                self.error("varName")
        
        elif token.recognized_string == "δήλωση":
            self.declarations()

    # sequence() updates the token at the end
    # so there is no need to call get_token()
    # after sequence() is called in the code
    def sequence(self):
        global token

        self.statement()
        
        while token.recognized_string == ";":
            token = self.get_token()

            self.statement()
        
    def statement(self):
        global token

        if token.family == "id":
            self.assignment_stat()

        elif token.recognized_string == "εάν":
            self.if_stat()

        elif token.recognized_string == "όσο":
            self.while_stat()

        elif token.recognized_string == "επανάλαβε":
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

    # CHANGED FOR INTERMEDIATE CODE
    def assignment_stat(self):
        global token
        
        var_name = token.recognized_string  # Save the variable name
        token = self.get_token()
        
        if token.recognized_string == ":=":
            token = self.get_token()
            
            expr_place = self.expression()
            # Generate assignment quad
            self.quad_list.genQuad(':=', expr_place, '_', var_name)
        else:
            self.error("assign")

    def if_stat(self):
        global token
        token = self.get_token()
        
        self.condition()

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

        if token.recognized_string == "αλλιώς":
            token = self.get_token()

            self.sequence()

    def while_stat(self):
        global token
        token = self.get_token()


        self.condition()

        if token.recognized_string == "επανάλαβε":
            token = self.get_token()

            self.sequence()

            if token.recognized_string != "όσο_τέλος":
                self.error("while-end")
            else:
                token = self.get_token()

    def do_stat(self):
        global token
        token = self.get_token()

        self.sequence()

        if token.recognized_string == "μέχρι":
            token = self.get_token()

            self.condition()

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

                if token.recognized_string == "έως":
                    token = self.get_token()

                    self.expression()
                    self.step()

                    if token.recognized_string == "επανάλαβε":
                        token = self.get_token()

                        self.sequence()

                        if token.recognized_string != "για_τέλος":
                            self.error("for-end")
                        else:
                            token = self.get_token()

                    else:
                        self.error("for-do")
                else:
                    self.error("for-range")
            else:
                self.error("assign")
        else:
            self.error("varName")

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
            self.error("varName")

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
            else:
                token = self.get_token()

    # just like sequence(), actualparlist() updates
    # the token at the end so there is no need to 
    # call get_token() after actualparlist() is called in the code
    def actualparlist(self):
        global token

        self.actualparitem()

        while token.recognized_string == ",":
            token = self.get_token()

            self.actualparitem()

    def actualparitem(self):
        global token

        if token.recognized_string != "%":
            self.expression()
        else:
            token = self.get_token()

            if token.family != "id":
                self.error("varName")
            else:
                token = self.get_token()

    # condition() updates the token at the end
    # like sequence() and actualparlist()
    def condition(self):
        global token

        self.boolterm()

        while token.recognized_string == "ή":
            token = self.get_token()

            self.boolterm()

    # boolterm() also updates the token at the end
    def boolterm(self):
        global token

        self.boolfactor()

        while token.recognized_string == "και":
            token = self.get_token()

            self.boolfactor()

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
                    token = self.get_token()
            else:
                self.error("sqBracketsOpen")
        
        elif token.recognized_string == "[":
            token = self.get_token()

            self.condition()

            if token.recognized_string != "]":
                self.error("sqBracketsClose")
            else:
                token = self.get_token()

        else:
            self.expression()
            self.relational_oper()
            self.expression()

    # expression() also updates the token at the end
    # CHANGED FOR INTERMEDIATE CODE
    def expression(self):
        global token
        
        # Take the first operand
        first_operand = self.term()

        while token.family == "addOperator":
            op = token.recognized_string  # Save the operator (+ or -)
            token = self.get_token()
            
            if token.family == "addOperator" or token.family == "mulOperator":
                self.error("operator")
                
            second_operand = self.term()
            
            # Generate quad for the addition/subtraction
            temp_result = self.new_temp()
            self.quad_list.genQuad(op, first_operand, second_operand, temp_result)
            first_operand = temp_result  # Update first_operand for chained operations
        
        return first_operand
    
    # CHANGED FOR INTERMEDIATE CODE
    def term(self):
        global token
        
        first_operand = self.factor()
        
        while token.family == "mulOperator":
            op = token.recognized_string  # Save the operator (* or /)
            token = self.get_token()
            
            if token.family == "addOperator" or token.family == "mulOperator":
                self.error("operator")
                
            second_operand = self.factor()
            
            # Generate quad for the multiplication/division
            temp_result = self.new_temp()
            self.quad_list.genQuad(op, first_operand, second_operand, temp_result)
            first_operand = temp_result  # Update first_operand for chained operations
            
        return first_operand

    # CHANGED FOR INTERMEDIATE CODE
    def factor(self):
        global token
        
        if token.family == "number":
            operand = token.recognized_string
            token = self.get_token()
            return operand
            
        elif token.recognized_string == "(":
            token = self.get_token()
            
            operand = self.expression()
            
            if token.recognized_string != ")":
                self.error("bracketsClose")
            else:
                token = self.get_token()
            return operand
            
        elif token.family == "id":
            operand = token.recognized_string
            token = self.get_token()
            
            if token.recognized_string == "(":
                self.idtail()
                temp = self.new_temp()
                return temp
            return operand

    def relational_oper(self):
        global token

        if token.family != "relationalOperator":
            self.error("relOp")
        else:
            token = self.get_token()
        
### ==================================



### ============= Quad =============
# Represents each quad, for example -> (1: + a b c)
class Quad:
    def __init__(self, label, op, op1, op2, op3):
        self.label = label
        self.op = op
        self.op1 = op1
        self.op2 = op2
        self.op3 = op3

    def __str__(self):
        return f"{self.label}: {self.op}, {self.op1}, {self.op2}, {self.op3}"

### ==================================


### ============= QuadPointer =============
# Used for the label of the quad, for example -> (1)
class QuadPointer:
    def __init__(self, label):
        self.label = label
    
    def __str__(self):
        return f"{self.label}"

### ==================================


### ============= QuadList =============
# Represents a list of quads an also holds the number of quads that have been created so far
class QuadList:
    def __init__(self):
        self.programList = []
        self.quad_counter = 1
        self.label_counter = 1

    def new_label(self):
        label = self.label_counter
        self.label_counter += 1
        return label

    def __str__(self):
        quad_strings = []
        for quad in self.programList:
            quad_strings.append(f"{quad.label}: {quad.op} {quad.op1}, {quad.op2}, {quad.op3}")
        return "\n".join(quad_strings)

    # Returns the next available quad number
    def nextQuad(self):
        return self.quad_counter
    
    # Generates a new quad and adds it to the program list
    def genQuad(self, op, op1, op2, op3):
        quad = Quad(
            label = self.quad_counter,
            op = op,
            op1 = op1,
            op2 = op2,
            op3 = op3
        )

        self.programList.append(quad)
        self.quad_counter += 1
        return quad.label


    # For each quad in list, we put label as op3
    # For example -> If list hold the quads [100, 102] then the "output" will be:
    # 100: jump, _, _, 104
    # 101: +, a, 1, a
    # 102: jump, _, _, 104
    # 103: +, a, 2, a
    def backPatch(self, quad_list, target_label):
        for quad_ptr in quad_list.labelList:
            quad_num = int(quad_ptr.label)        
            self.programList[quad_num - 1].op3 = target_label


### ==================================


### ============= QuadPointerList =============
class QuadPointerList:
    def __init__(self):
        self.labelList = []

    def __str__(self):
        return ",".join(str(qp) for qp in self.labelList)

    def add(self, label):
        self.labelList.append(QuadPointer(label))

    def merge(self, other_list):
        merged = QuadPointerList()
        merged.labelList = self.labelList + other_list.labelList
        return merged

### ==================================



def main():
    start = timer()
    lexer = Lexer(source_file)

    parser = Parser(lexer)
    parser.syntax_analyzer()

    # Print generated quads
    print("\nGenerated Intermediate Code:")
    print(parser.quad_list)

    end = timer()
    print("Compiled successfuly in: {:.4f} seconds".format(end - start))

main()