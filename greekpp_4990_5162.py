import sys
import string

### ============= Helper Functions =============
def categorize(char):
    if char.isalpha() or char == '_':
        return "alpha"
    elif char.isnumeric():
        return "digit"
    elif char == '+' or char == '-' or char == '*' or char == '/':
        return "arithmOp"
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
    elif char == '{' or char == '}':
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

    def __error(self, case):
        print("Lexer error in line: " + str(line_number))

        if case == "number":
            print("\tIllegal number constant. Can not contain non-numerical values")
        elif case == "limits":
            print("\tIllegal length of variable name")
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
                        self.__error("limits")
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
                        self.__error("number")
                    if self.line_index >= len(current_line):
                        break

                    char = current_line[self.line_index]
                    category = categorize(char)

                family = "number"
                break

            elif category == "delimiter":
                current_string += char
                self.line_index += 1

                family = "delimiter"
                break

            elif category == "arithmOp":
                current_string += char
                self.line_index += 1
                
                family = "arithmOperator"
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
                    self.__error("assign")
            
            elif category == "group":
                current_string += char
                self.line_index += 1

                family = "group"
                break

            elif category == "comment":
                if char == '{':
                    while not char == "}":
                        self.line_index += 1
                        char = current_line[self.line_index]

                        if char == '\n':
                            line_number += 1
                            self.line_index = 0

                            char = current_line[self.line_index]
                        elif char == '':
                            self.__error("EOF")
                            break
                    
                    break

                else:
                    self.__error("unknown")
                    break

            elif category == "pointer":
                current_string += char
                self.line_index += 1

                family = "pointer"
                break

            elif category == "character error":
                self.__error("unknown")
            else:
                self.__error("unknown")

        next_token = Token(current_string, family, line_number)
        print(next_token)
        return next_token
    
### =================================

def main():
    lexer = Lexer(sys.argv[1])
    lexer.nextToken()
    lexer.nextToken()
    lexer.nextToken()
    lexer.nextToken()
    lexer.nextToken()
    lexer.nextToken()
    lexer.nextToken()
    lexer.nextToken()
    lexer.nextToken()
    lexer.nextToken()
    lexer.nextToken()

main()