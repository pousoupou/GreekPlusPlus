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

                if int(current_string) < -99999 or int(current_string) > 99999:
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

            elif category == "equal":
                current_string += char
                self.line_index += 1

                family = "relationalOperator"
                break
            
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
        self.sym_table = SymbolTable()
        self.code_generator = CodeGenerator(self.sym_table)

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

    #CHANGED FOR INTERMEDIATE CODE
    #CHANGED FOR SYMBOL TABLE
    def program(self):
        global token
        
        if token.recognized_string == "πρόγραμμα":
            token = self.get_token()
            
            if token.family == "id":
                global progName
                progName = token.recognized_string #Store the name to use later

                # Enter program scope
                self.sym_table.enter_scope()

                token = self.get_token()
                self.program_block()

            else:
                self.error("name")
        else:
            self.error("program")

    #CHANGED FOR INTERMEDIATE CODE
    #CHANGED FOR FINAL CODE
    def program_block(self):
        global token

        self.code_generator.beginBlock()

        self.declarations()

        self.subprograms()

        Quad.genQuad('begin_block', progName, '_', '_')

        self.code_generator.beginMain()

        if token.recognized_string == "αρχή_προγράμματος":
            token = self.get_token()

            self.sequence()
        else:
            self.error("start")

        if token.recognized_string != "τέλος_προγράμματος":
            self.error("end")

        Quad.genQuad('halt', '_', '_', '_')
        Quad.genQuad('end_block', progName, '_', '_')
        self.sym_table.exit_scope()

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
    # CHANGED FOR SYMBOL TABLE
    def varlist(self):
        global token
        
        if token.family == "id":
            while token.family == "id":
                var = Entity(token.recognized_string)
                # Add variable to symbol table
                self.sym_table.addEntity(var)

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

    #CHANGED FOR INTERMEDIATE CODE
    #CHANGED FOR SYMBOL TABLE
    def func(self):
        global token

        if token.family == "id":
            global funcName
            funcName = token.recognized_string

            # Add function to the symbol table
            func_entity = Entity(funcName, 'function')
            self.sym_table.addEntity(func_entity)

            # Enter function scope
            self.sym_table.enter_scope()

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

    #CHANGED FOR INTERMEDIATE CODE
    #CHANGED FOR SYMBOL TABLE
    def proc(self):
        global token

        if token.family == "id":
            global procName
            procName = token.recognized_string

            # Add procedure to symbol table
            proc_entity = Entity(procName, 'procedure')
            self.sym_table.addEntity(proc_entity)

            # Enter procedure scope
            self.sym_table.enter_scope()

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

    #CHANGED FOR SYMBOL TABLE
    def formalparlist(self):
        global token
        self.parameter_names = []

        if token.family == "id":
            while token.family == "id":
                self.parameter_names.append(token.recognized_string)
                token = self.get_token()

                if token.recognized_string == ",":
                    token = self.get_token()
                else:
                    break
            
        elif token.recognized_string != ")":
            self.error("parList")

    #CHANGED FOR INTERMEDIATE CODE
    # CHANGED FOR FINAL CODE
    def funcblock(self):
        global token

        current_func_name = funcName

        if token.recognized_string == "διαπροσωπεία":
            token = self.get_token()

            self.funcinput()
            self.funcoutput()
            self.declarations()
            self.subprograms()

            func = Quad.genQuad('begin_block', current_func_name, '_', '_')

            # entity = Entity(funcName)
            # self.sym_table.addEntity(entity)
            scope = self.sym_table.table[nesting_level-1]
            scope.entities[len(scope.entities)-1].set_start_quad(func)

            self.code_generator.beginBlock()

            if token.recognized_string == "αρχή_συνάρτησης":
                token = self.get_token()

                self.sequence()

                if token.recognized_string != "τέλος_συνάρτησης":
                    self.error("func-end")
            
            else:
                self.error("func-start")

            end_quad = Quad.genQuad('end_block', current_func_name, '_', '_')
            scope = self.sym_table.table[nesting_level-1]
            scope.entities[len(scope.entities)-1].set_frame_length(func, end_quad)

            self.sym_table.exit_scope()

            self.code_generator.endBlock()

        else:
            self.error("func-interface")

    #CHANGED FOR INTERMEDIATE CODE
    # CHANGE FOR FINAL CODE
    def procblock(self):
        global token

        current_proc_name = procName

        if token.recognized_string == "διαπροσωπεία":
            token = self.get_token()

            self.funcinput()
            self.declarations()
            self.subprograms()

            proc = Quad.genQuad('begin_block', current_proc_name, '_', '_')
            scope = self.sym_table.table[nesting_level-1]
            scope.entities[len(scope.entities)-1].set_start_quad(proc)

            self.code_generator.beginBlock()
            
            if token.recognized_string == "αρχή_διαδικασίας":
                token = self.get_token()

                self.sequence()

                if token.recognized_string != "τέλος_διαδικασίας":
                    self.error("proc-end")
            else:
                self.error("proc-start")

            end_quad = Quad.genQuad('end_block', procName, '_', '_')
            scope = self.sym_table.table[nesting_level-1]
            scope.entities[len(scope.entities)-1].set_frame_length(proc, end_quad)

            self.sym_table.exit_scope()
            
            self.code_generator.endBlock()

        else:
            self.error("proc-interface")

    # CHANGED FOR SYMBOL TABLE
    def funcinput(self):
        global token

        if token.recognized_string == "είσοδος":
            token = self.get_token()

            while token.family == "id":
                name = token.recognized_string

                # Add the formal parameters in symbol table
                if name not in self.parameter_names:
                    self.error(f"{name} didnt find it in the formal param list")

                entity = Entity(name, None, 'in')
                self.sym_table.addEntity(entity)
                self.sym_table.addArg(entity)

                token = self.get_token()
                if token.recognized_string == ",":
                    token = self.get_token()
                else:
                    break
            else:
                self.error("varName")
        
        elif token.recognized_string == "έξοδος":
            self.funcoutput()

        elif token.recognized_string == "δήλωση":
            self.declarations()

    # CHANGED FOR SYMBOL TABLE
    def funcoutput(self):
        global token

        if token.recognized_string == "έξοδος":
            token = self.get_token()

            while token.family == "id":
                name = token.recognized_string

                # Add the formal parameters in symbol table
                if name not in self.parameter_names:
                    self.error(f"{name} didnt find it in the formal param list")

                entity = Entity(name, None, 'out')
                self.sym_table.addEntity(entity)
                self.sym_table.addArg(entity)

                token = self.get_token()
                if token.recognized_string == ",":
                    token = self.get_token()
                else:
                    break
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
    # CHANGED FOR FINAL CODE
    def assignment_stat(self):
        global token
        
        var_name = token.recognized_string  # Save the variable name
        token = self.get_token()
        
        if token.recognized_string == ":=":
            token = self.get_token()
            
            expr_place = self.expression()

            # Generate assignment quad
            Quad.genQuad(':=', expr_place, '_', var_name)

            self.code_generator.generateAssignment(expr_place, var_name)

        else:
            self.error("assign")

    #CHANGED FOR INTERMEDIATE CODE
    def if_stat(self):
        global token
        token = self.get_token()
        
        # Evaluate the condition
        trueList, falseList = self.condition()

        # Backpatch true jumps to then-block
        Quad.backPatch(trueList, Quad.nextQuad())

        if token.recognized_string == "τότε":
            token = self.get_token()
            
            # Process the then-block
            self.sequence()
            
            # Create jump to skip else-block (will be backpatched to end of if)
            after_then_jump = Quad.makeList(Quad.nextQuad())
            Quad.genQuad('jump', '_', '_', '_')
            
            # Backpatch false jumps to else-block
            else_label = Quad.nextQuad()
            Quad.backPatch(falseList, else_label)

            # Process the else-block statements
            self.elsepart()

            # Backpatch jumps after then-block to end of if
            end_label = Quad.nextQuad()
            Quad.backPatch(after_then_jump, end_label)

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

    #CHANGED FOR INTERMEDIATE CODE
    def while_stat(self):
        global token
        token = self.get_token()

        #Start label for the loop
        start_label = Quad.nextQuad()

        # Evaluate the condtion
        trueList, falseList = self.condition()

        # Backpatch true jumps to loop body
        Quad.backPatch(trueList, Quad.nextQuad())

        if token.recognized_string == "επανάλαβε":
            token = self.get_token()

            # Process the loop body
            self.sequence()

            # Jump back to condition evaluation 
            Quad.genQuad('jump', '_', '_', start_label)

            # Backpatch false jumps to exit the loop
            end_label = Quad.nextQuad()
            Quad.backPatch(falseList, end_label)

            if token.recognized_string != "όσο_τέλος":
                self.error("while-end")
            else:
                token = self.get_token()
        else:
            self.error("επανάλαβε expected after condition")

    #CHANGED FOR INTERMEDIATE CODE
    def do_stat(self):
        global token
        token = self.get_token()

        #Label for the start of the loop
        start_label = Quad.nextQuad()

        # Process the loop body
        self.sequence()

        if token.recognized_string == "μέχρι":
            token = self.get_token()
            

            # Evaluate the condition. False -> continue loop
            trueList, falseList = self.condition()

            # Backpatch false jumps to the start of the loop
            Quad.backPatch(falseList, start_label)

            # Backpatch true jumps to exit the loop
            end_label = Quad.nextQuad()
            Quad.backPatch(trueList, end_label)
        else:
            self.error("do-end")

    #CHANGED FOR INTERMEDIATE CODE
    def for_stat(self):
        global token
        token = self.get_token()

        if token.family == "id":
            counter_var = token.recognized_string
            token = self.get_token()

            if token.recognized_string == ":=":
                token = self.get_token()

                initial_value = self.expression()
                Quad.genQuad(':=', initial_value, '_', counter_var)

                if token.recognized_string == "έως":
                    token = self.get_token()

                    final_value = self.expression()
                    
                    if token.recognized_string == "με_βήμα":
                        token = self.get_token()
                        step_value = self.expression()

                    # Start of the loop
                    start_label = Quad.nextQuad()
                    
                    # Condition check
                    temp = Quad.newTemp()
                    Quad.genQuad('<=', counter_var, final_value, temp)
                    self.sym_table.addEntity(Entity(temp))

                    # Create jump for loop exit
                    exit_list = Quad.makeList(Quad.nextQuad())
                    exit_list.append(Quad.genQuad('jump', '_', '_', temp))

                    if token.recognized_string == "επανάλαβε":
                        token = self.get_token()

                        self.sequence()
        
                        increment_temp = Quad.newTemp()
                        Quad.genQuad('+', counter_var, step_value, increment_temp)
                        Quad.genQuad(':=', increment_temp, '_', counter_var)
                        
                        self.sym_table.addEntity(Entity(increment_temp))

                        # Jump back to condition check
                        Quad.genQuad('jump', '_', '_', start_label)
                        
                        # Backpatch exit jumps
                        exit_label = Quad.nextQuad()
                        Quad.backPatch(exit_list, exit_label)

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

    #CHANGED FOR INTERMEDIATE CODE
    def input_stat(self):
        global token
        token = self.get_token()

        if token.family == "id":
            in_var = token.recognized_string
            Quad.genQuad('in', in_var, '_', '_')
            token = self.get_token()
        else:
            self.error("varName")

    #CHANGED FOR INTERMEDIATE CODE
    def print_stat(self):
        global token
        token = self.get_token()

        expr_result = self.expression()
        Quad.genQuad('out', expr_result, '_', '_')

    #CHANGED FOR INTERMEDIATE CODE
    # CHANGED FOR FINAL CODE
    def call_stat(self):
        global token

        token = self.get_token()

        if token.family == "id":
            func_name = token.recognized_string
            token = self.get_token()

            self.idtail()

            Quad.genQuad('call', func_name, '_', '_')

            self.code_generator.generateCall(func_name)
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
    # CHANGED FOR FINAL CODE
    def actualparlist(self):
        global token

        self.param_counter = 0 # Counter for the position of each parameter

        self.actualparitem()

        while token.recognized_string == ",":
            token = self.get_token()

            self.actualparitem()

    # CHANGED FOR INTERMEDIATE CODE
    # CHANGED FOR FINAL CODE
    def actualparitem(self):
        global token

        if token.recognized_string != "%":
            # (CV)
            expr_place = self.expression()

            if expr_place != None:
                Quad.genQuad('par', expr_place, 'CV', '_')

            self.code_generator.generateParameters(expr_place, 'CV', self.param_counter)

            self.param_counter += 1
        else:
            # (REF)
            token = self.get_token()
            if token.family != "id":
                self.error("varName")
            else:
                var_name = token.recognized_string
                
                Quad.genQuad('par', var_name, 'REF', '_')

                self.code_generator.generateParameters(var_name, 'REF', self.param_counter)

                self.param_counter += 1

                token = self.get_token()

    # condition() updates the token at the end
    # like sequence() and actualparlist()
    #CHANGED FOR INTERMEDIATE CODE
    def condition(self):
        global token

        # Get the first boolterm
        trueList, falseList = self.boolterm()

        while token.recognized_string == "ή":
            token = self.get_token()

            # If previous is false then continue to the next term
            Quad.backPatch(falseList, Quad.nextQuad())
            
            # Evaluate the next term
            next_trueList, next_falseList = self.boolterm()

            # If anything from the first or second term is true then the expression is true
            trueList = Quad.merge(trueList, next_trueList)

            # If both terms are false then the expression is false
            falseList = next_falseList

        return (trueList, falseList)

    # boolterm() also updates the token at the end
    #CHANGED FOR INTERMEDIATE CODE
    def boolterm(self):
        global token

        # First boolean factor
        trueList, falseList = self.boolfactor()

        while(token.recognized_string == "και"):
            token = self.get_token()

            # Backpatch previous trueList to current position (so if previous is true, continue)
            Quad.backPatch(trueList, Quad.nextQuad())

            # Evaluate the next factor
            next_trueList, next_falseList = self.boolfactor()

            # If anything from the first factor is false then the whole expression is false
            falseList = Quad.merge(falseList, next_falseList)

            # If the first one is true then check the next
            trueList = next_trueList

        return (trueList, falseList)

    # CHANGED FOR INTERMEDIATE CODE
    def boolfactor(self):
        global token

        if token.recognized_string == "όχι":
            token = self.get_token()

            if token.recognized_string == "[":
                token = self.get_token()

                #Get the condition result
                trueList, falseList = self.condition()
                
                if token.recognized_string != "]":
                    self.error("sqBracketsClose")
                else:
                    token = self.get_token()
                    return(falseList, trueList) # SWAP BECAUSE OF NOT
                            
            else:
                self.error("sqBracketsOpen")

        elif token.recognized_string == "[":
            token = self.get_token()

            # Get the condition result
            trueList, falseList = self.condition()

            if token.recognized_string != "]":
                self.error("sqBracketsClose")
            else:
                token = self.get_token()

            return (trueList, falseList)

        else:
            left_expr = self.expression()
            rel_op = token.recognized_string
            token = self.get_token()
            right_expr = self.expression()

            #Generate the quad for relational operation
            trueList = Quad.makeList(Quad.nextQuad())
            Quad.genQuad(rel_op, left_expr, right_expr, '_')

            # Create false list for the jump after the expression
            falseList = Quad.makeList(Quad.nextQuad())
            Quad.genQuad('jump', '_', '_', '_')

            return (trueList, falseList)

    # expression() also updates the token at the end
    # CHANGED FOR INTERMEDIATE CODE
    # CHANGED FOR FINAL CODE
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
            temp_result = Quad.newTemp()
            self.sym_table.addEntity(Entity(temp_result))

            Quad.genQuad(op, first_operand, second_operand, temp_result)

            self.code_generator.generateArithmetic(op, first_operand, second_operand, temp_result)

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
            temp_result = Quad.newTemp()
            self.sym_table.addEntity(Entity(temp_result))

            Quad.genQuad(op, first_operand, second_operand, temp_result)
            first_operand = temp_result  # Update first_operand for chained operations
            
        return first_operand

    # CHANGED FOR INTERMEDIATE CODE
    def factor(self):
        global token
        
        # Handle optional sign (+ or -)
        if token.family == "addOperator":
            op = token.recognized_string
            token = self.get_token()

            # Get the operand
            operand = self.factor()

            # Handle the -
            if op == '-':
                temp = Quad.newTemp()
                Quad.genQuad('-', '0', operand, temp) # The -α is (0 - α)
                self.sym_table.addEntity(Entity(temp))
                return temp
            
            # Just return the operand if it's +
            return operand

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
            

        # If factor -> id idtail
        elif token.family == "id":
            operand = token.recognized_string
            token = self.get_token()
            
            # Function or procedure call (it has '(' )
            if token.recognized_string == "(":
                temp = Quad.newTemp()
                self.sym_table.addEntity(Entity(temp))
                self.idtail()
                return temp
            
            return operand

    def relational_oper(self):
        global token

        if token.family != "relationalOperator":
            self.error("relOp")
        else:
            token = self.get_token()
        
### ==================================

### =============== Intermediary Code ===================

label = 0
temp = 0
interCode = []

class Quad:
    def __init__(self, op, arg1, arg2, arg3):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        global label
        label += 1
        self.label = label

    def __str__(self):
        return f"{self.label} : {self.op} , {self.arg1} , {self.arg2} , {self.arg3}"
    
    @staticmethod
    def nextQuad():
        global label
        return label + 1
    
    @staticmethod
    def genQuad(op, arg1, arg2, arg3):
        quad = Quad(op, arg1, arg2, arg3)

        global interCode
        interCode.append(quad)

        return quad.label
    
    @staticmethod
    def newTemp():
        global temp
        temp += 1

        return f"t@{temp}"

    @staticmethod
    def emptyList():
        return []
    
    @staticmethod
    def makeList(quad_label):
        return [quad_label]
    
    @staticmethod
    def merge(list1, list2):
        return list1 + list2
    
    @staticmethod
    def backPatch(label_list, target_label):
        global interCode
        for quad in interCode:
            if quad.label in label_list:
                quad.arg3 = target_label

### =====================================================

### =============== Symbol Table ====================
class Entity:
    def __init__(self, name, value = None, par_mode = None, start_quad = None, args = [], frame_length = None):
        self.name = name
        self.value = value
        self.par_mode = par_mode
        self.start_quad = start_quad
        self.args = args
        self.frame_length = frame_length

    def __str__(self):
        return f"{self.name} : {self.start_quad} : {self.args} : {self.frame_length} : {self.par_mode} : {self.value} : {self.offset}"

    def set_start_quad(self, quad):
        self.start_quad = quad + 1

    def set_frame_length(self, start, end):
        length = end - start
        self.frame_length = length + self.offset

nesting_level = -1 # THE GLOBAL SCOPE IS 0
class Scope:
    def __init__(self):
        self.entities = []
        global nesting_level
        nesting_level += 1
        self.nesting_level = nesting_level
        self.offset = 12

    def close(self):
        global nesting_level
        # self.print()
        nesting_level -= 1

    def print(self):
        global nesting_level
        output = "Scope: " + str(self.nesting_level) + "\n"

        for entity in self.entities:
            if(entity.name != None):
                output += "name: " + str(entity.name) + ", "
            if(entity.value != None):
                output += "value: " + str(entity.value) + ", "
            if(entity.par_mode != None):
                output += "par_mode: " + str(entity.par_mode) + ", "
            if(entity.start_quad != None):
                output += "start_quad: " + str(entity.start_quad) + ", "
                if(entity.args != None):
                    output += "args: " + str(entity.args) + ", "
                if(entity.frame_length != None):
                    output += "frame_length: " + str(entity.frame_length) + ", "
                output += "\n"
                continue
            if(entity.offset != None):
                output += "offset: " + str(entity.offset) + ", "
            
            output += "\n"

        print(output)

class Argument:
    def __init__(self, par_mode):
        self.par_mode = par_mode

class SymbolTable:
    def __init__(self):
        self.table = []

    def get_scope(self, nesting_level):
        if nesting_level in self.table:
            return self.table[nesting_level]
        else:
            return None
        
    def enter_scope(self):
        scope = Scope()
        self.table.append(scope)

    def exit_scope(self):
        if len(self.table) > 0:
            scope = self.table.pop()
            scope.close()
    
    def addEntity(self, entity):
        scope = self.table.pop()
        entity.offset = scope.offset
        scope.offset += 4
        scope.entities.append(entity)
        self.table.append(scope)

    def addArg(self, entity):
        scope = self.table.pop()
        scope.entities[len(scope.entities)-1].args.append(entity.par_mode)
        self.table.append(scope)

    def lookup(self, name):
        for scope in reversed(self.table):
            for entity in scope.entities:
                if entity.name == name:
                    return entity, scope.nesting_level
        return None, None

### =================================================

### =============== Final Code ====================
finalCode = []
is_first = True

class CodeGenerator:
    def __init__(self, sym_table):
        self.sym_table = sym_table
        self.label_counter = 0

    def gnlvcode(self, variable):
        global finalCode

        entity, variable_scope_level = self.sym_table.lookup(variable)
        # If we didnt find the variable in symbol table
        if entity is None:
            print(f"Did not find variable {variable}")
            return
        
        current_scope_level = len(self.sym_table.table) - 1 # Current nesting level

        finalCode.append("lw t0, -4(sp)") # Go to the parent

        # Move up as many times as needed 
        for i in range(current_scope_level - 1, variable_scope_level, -1):
            finalCode.append("lw t0, -4(t0)")

        # Move t0 down by offset
        finalCode.append(f"addi t0, t0, -{entity.offset}")

    #TODO: Check pg.27 for if conds in line 1488. gp (global pointer) mentioned but not used
    #TODO: Achually, this implementation is wrong. Stuff from pg.30 are missing
    def loadvr(self, variable, destination_reg):
        global finalCode

        entity, variable_scope_level = self.sym_table.lookup(variable)

        # If we didnt find the variable in symbol table
        if entity is None and (not variable.isdigit()): #TODO: why .isdigit() ?
            print(f"Did not find variable {variable}")
            return
        
        current_scope_level = len(self.sym_table.table) - 1 # Current scope level

        # Variable is arithmetic constant
        if variable.isdigit():
            finalCode.append(f"li {destination_reg}, {variable}")

        # If variable is global
        elif variable_scope_level == 0 and current_scope_level != variable_scope_level:
            finalCode.append(f"lw {destination_reg}, -{entity.offset}(gp)")

        elif variable_scope_level == 0 and current_scope_level == variable_scope_level:
            finalCode.append(f"lw {destination_reg}, -{entity.offset}(sp)")

        # If variable is local, or is formal parameter by value, or is temp variable AND is in current scope
        elif current_scope_level == variable_scope_level and (entity.par_mode == 'None' or entity.par_mode == 'in' or variable.startswith('t@')):
            finalCode.append(f"lw {destination_reg}, -{entity.offset}(sp)")
        
        # If variable is formal parameter by reference AND is in current scope
        elif current_scope_level == variable_scope_level and entity.par_mode == 'out':
            finalCode.append(f"lw t0, -{entity.offset}(sp)")
            finalCode.append(f"lw {destination_reg}, (t0)")

        # If variable is not in current scope and in it's scope it's local variable or it's formal parameter by value
        elif current_scope_level != variable_scope_level and (entity.par_mode == 'None' or entity.par_mode == 'in'):
            self.gnlvcode(variable)
            finalCode.append(f"lw {destination_reg}, (t0)")

        # If variable is not in current scope and in it's scope it's formal parameter by reference
        elif current_scope_level != variable_scope_level and entity.par_mode == 'out':
            self.gnlvcode(variable)
            finalCode.append(f"lw t0, (t0)")
            finalCode.append(f"lw {destination_reg}, (t0)")

    def storevr(self, destination_reg, variable):
        global finalCode

        entity, variable_scope_level = self.sym_table.lookup(variable)

        # If we didnt find the variable in symbol table
        if entity is None and (not variable.isdigit()):
            print(f"Did not find variable {variable}")
            return
        
        current_scope_level = len(self.sym_table.table) - 1 # Current scope level

        # If variable is global
        if variable_scope_level == 0 and current_scope_level != variable_scope_level:
            finalCode.append(f"sw {destination_reg}, -{entity.offset}(gp)")

        elif variable_scope_level == 0 and current_scope_level == variable_scope_level:
            finalCode.append(f"sw {destination_reg}, -{entity.offset}(sp)")

        # If variable is local, or is formal parameter by value, or is temp variable AND is in current scope
        elif current_scope_level == variable_scope_level and (entity.par_mode == 'None' or entity.par_mode == 'in' or variable.startswith('t@')):
            finalCode.append(f"sw {destination_reg}, -{entity.offset}(sp)")

        # If variable is formal parameter by reference AND is in current scope
        elif current_scope_level == variable_scope_level and entity.par_mode == 'out':
            finalCode.append(f"lw t0, -{entity.offset}(sp)")
            finalCode.append(f"sw {destination_reg}, (t0)")

        # If variable is in scope < current scope and in it's scope it's local variable or it's formal parameter by value
        elif current_scope_level > variable_scope_level and (entity.par_mode == 'None' or entity.par_mode == 'in'):
            self.gnlvcode(variable)
            finalCode.append(f"sw {destination_reg}, (t0)")

        # If variable is in scope < current scope and in it's scope it's formal parameter by reference
        elif current_scope_level > variable_scope_level and entity.par_mode == 'out':
            self.gnlvcode(variable)
            finalCode.append(f"lw t0, (t0)")
            finalCode.append(f"sw {destination_reg}, (t0)")

    def generateAssignment(self, source, destination):
        global finalCode

        # Print the label
        finalCode.append(self.newLabel())

        # Load source
        self.loadvr(source, 't1')

        # Store destination
        self.storerv('t1', destination)

    def generateArithmetic(self, op, x, y, z):
        global finalCode

        # Print the label
        finalCode.append(self.newLabel())

        # Load x
        self.loadvr(x, 't1')

        # Load y
        self.loadvr(y, 't2')

        # Perform operation
        if op == '+':
            finalCode.append("add t1, t1, t2")
        elif op == '-':
            finalCode.append("sub t1, t1, t2")
        elif op == '/':
            finalCode.append("div t1, t1, t2")
        else:
            finalCode.append("mul t1, t1, t2")

        # Store result
        self.storerv('t1', z)

    # For function parameters
    def generateParameters(self, parameter, mode, counter):
        global finalCode

        entity, parameter_scope_level = self.sym_table.lookup(parameter)

        if entity:
            finalCode.append(f"{self.newLabel()}")

            # Find current scope
            testScope = None
            for scope in self.sym_table.table:
                if scope.nesting_level == parameter_scope_level:
                    testScope = scope

            # Find the max offset of variables in this scope
            if testScope:
                max_offset = 0
                for e in testScope.entities:
                    if e.value == None:
                            if e.offset > max_offset:
                                max_offset = e.offset

            if mode == 'CV':
                finalCode.append(f"addi fp, sp, {max_offset}")
                self.loadvr(parameter, 't0')
                finalCode.append(f"sw t0, -{12 + (4 * counter)}(fp)")
            
            elif mode == 'REF':
                finalCode.append(f"addi t0, sp, -{entity.offset}")
                finalCode.append(f"sw t0, -{12 + (4 * counter)}(fp)")

    def generateCall(self, function_name):
        global finalCode

        func, func_scope_level = self.sym_table.lookup(function_name)

        current_scope_level = len(self.sym_table.table) - 1

        finalCode.append(f"{self.newLabel()}")

        if func_scope_level == current_scope_level:
            finalCode.append(f"sw sp, -4(fp)")
        else:
            finalCode.append(f"lw t0, -4(sp)")
            finalCode.append(f"sw t0, -4(fp)")

        finalCode.append(f"addi sp, sp, {func.frame_length}")
        finalCode.append(f"jal L1")
        finalCode.append(f"addi sp, sp, -{func.frame_length}")

    # Generate new labels for final code
    def newLabel(self):
        label = f"L{self.label_counter}:"
        self.label_counter += 1
        return label
            
    def beginBlock(self):
        global finalCode
        global is_first
        if is_first:
            # Only for the first function (in the deeper scope)
            finalCode.append(f"{self.newLabel()} j Lmain")
            is_first = False
        else:
            finalCode.append(f"{self.newLabel()} sw ra, -0(sp)")

    def endBlock(self):
        global finalCode

        finalCode.append(f"{self.newLabel()}")
        finalCode.append("lw ra, -0(sp)")
        finalCode.append("jr ra")

    def beginMain(self):
        global finalCode

        finalCode.append("Lmain:")
        finalCode.append(f"{self.newLabel()}")

        # Find global scope
        global_scope = None
        for scope in self.sym_table.table:
            if scope.nesting_level == 0:
                global_scope = scope
                break

        # Find the offset that we need to add to sp
        if global_scope:
            max_offset = 0
            for entity in global_scope.entities:
                if entity.value == None:
                    if entity.offset > max_offset:
                        max_offset = entity.offset

            stack_offset = max_offset + 4

        finalCode.append(f"addi sp, sp, {stack_offset}")
        finalCode.append(f"move gp, sp")
### =================================================

def main():
    start = timer()
    lexer = Lexer(source_file)

    parser = Parser(lexer)
    parser.syntax_analyzer()

    fd = open(progName + ".int", "w", encoding="utf-8") # Encoding for greek letters

    for quad in interCode:
        fd.write(str(quad) + "\n")
        # print(quad)

    fd.close()

    fd = open(progName + ".asm", "w", encoding="utf-8") # Encoding for greek letters
    for line in finalCode:
        fd.write(line + "\n")

    fd.close()

    end = timer()
    print("Compiled successfuly in: {:.4f} seconds".format(end - start))

main()