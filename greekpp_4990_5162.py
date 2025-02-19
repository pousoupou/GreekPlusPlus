# -*- coding: utf-8 -*-

import sys
import string

### ============= Helper Functions =============
def open_gpp_source_file(file_name):
    return open(file_name, 'r')

def close_gpp_source_file(file_name):
    file_name.close()

def categorize(char):
    if char.isalpha():
        return "alpha"
    elif char.isnumeric():
        return "digit"
    elif char == '+' or char == '-' or char == '*' or char == '/':
        return "arithmOp"
    elif char == '<':
        return "smaller"
    elif char == '>':
        return "bigger"
    elif char == ':':
        return "asgn"
    elif char == "=":
        return "relationOp"
    elif char == ';' or char == ',':
        return "delimiter"
    elif char == '(' or char == ')' or char == '[' or char == ']':
        return "group"
    elif char == '{' or char == '}':
        return "comment"
    elif char == '%':
        return "pointer"
    elif char == '':
        return "EOF"
    else:
        return "character error"
    


### ============================================

### ============= Lexer =============

## ==== Global Definitions ====
line_number = 1

state = "start"

keywords = (
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
)

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
        return self.recognized_string + "\t family: " + self.family + "\t line: " + str(self.line_number)

## ============================

def lexer():
    source_file = sys.argv[1]
    fd = open_gpp_source_file(source_file)

    token = Token()

    char = ''
    while not (char == '\n' or char == ' ' or char == '\t'):
        char = fd.read(1)
        token.recognized_string += char

        category = categorize(char)

        if (state == "start" and category == "alpha"):
            state = "idk"
        elif (state == "start" and category == "digit"):
            state = "dig"
        elif (state == "start" and category == "arithmOp"):
            state == "arithmetic Operator"
        elif (state == "start" and category == "asgn"):
            state == "assignment"
        elif (state == "start" and category == "delimiter"):
            state == "delimiter"
        elif (state == "start" and category == "group"):
            state = "group"
        elif (state == "start" and category == "bigger"):
            state = "bigger"
        elif (state == "start" and category == "smaller"):
            state = "smaller"
        elif (state == "start" and category == "relationOp"):
            state = "relation Operator"
        elif (state == "start" and category == "comment"):
            state = "comment"
        elif (state == "start" and category == "pointer"):
            state = "pointer"
        elif (state == "start" and category == "EOF"):
            state = "EOF"
        elif (state == "start" and category == "character error"):
            state = "character error"
        elif (state == "idk" and (category == "alpha" or category == "digit")):
            state = "idk"
        elif state == "idk" and 
        else:
            state = "unknown error"

    if char == '\n':
        line_number += 1



    close_gpp_source_file(source_file)

### =================================
