import string

# BibTeX grammar (rough, used to create the parser below)
# <S> ::= <entry-list>
# <entry-list> ::= <entry> <entry_list>
#                | <entry> 
# <entry> ::= "@" string (type) "{" string (cite-key) "," <field-list> "}"
# <field-list> ::= <field> "," <field-list>
#                | <field>
# <field> ::= string (name) "=" <field-value>
# <field-value> ::= "{"|"\"" string (value) "}"|"\""
#                 | integer

# TODO 

# recurse into nested {} ?
# handle # by grammar rule = allow foo # bar # bat

# - handle {} nested eg title = {Some {Dangerous} Sea Excursions}, author={{Ben}}
# - strict mode
# - tests
#   - round-trip
# http://www.bibtex.org/SpecialSymbols/
# @string, @preamble, @comment
# case sensitivity / insensitivity

EXPAND = {}

class _bibtex_tokenlist(list):
    def __getitem__(self, key):
        try:
            ret = super().__getitem__(key)
        except IndexError:
            raise Exception("parse error, tokens = {}".format(self))
        return ret

def bibtex_parse(bibtex_str):
    return _bibtex_parse_s(bibtex_str)

def bibtex_tokenize(bibtex_str):
    token_stack = _bibtex_tokenlist()
    i = 0
    curly_nesting_depth = 0
    bibtex_str_len = len(bibtex_str)
    boundary_chars = string.whitespace + '@=,"{}()'

    while i < bibtex_str_len:
        if bibtex_str[i] in string.whitespace:
            i += 1
            continue
        if bibtex_str[i] in ('@', '=', ','):
            token_stack.append(bibtex_str[i])
            i += 1
            continue
        if bibtex_str[i] == '"':
            token_stack.append('"')
            i += 1
            tmp = ''
            while i < bibtex_str_len and bibtex_str[i] != '"':
                tmp += bibtex_str[i]
                i += 1
            if tmp != '':
                token_stack.append(tmp)
            token_stack.append('"')
            i += 1
            continue
        old_curly_nesting_depth = curly_nesting_depth
        if curly_nesting_depth > 0 and bibtex_str[i] in ('{', '('):
            curly_nesting_depth += 1
            token_stack.append(bibtex_str[i])
            i += 1
            tmp = ''
            while i < bibtex_str_len and curly_nesting_depth != old_curly_nesting_depth: 
                tmp += bibtex_str[i]
                if bibtex_str[i] in ('{', '('):
                    curly_nesting_depth += 1
                if bibtex_str[i] in ('}', ')'):
                    curly_nesting_depth -= 1
                i += 1
            if tmp != '':
                tmp = tmp[:-1]
                token_stack.append(tmp)
                token_stack.append(bibtex_str[i-1])
            continue
        if bibtex_str[i] in ('{', '('):
            curly_nesting_depth += 1
            token_stack.append(bibtex_str[i])
            i += 1
            continue
        if bibtex_str[i] in ('}', ')'):
            curly_nesting_depth -= 1
            token_stack.append(bibtex_str[i])
            i += 1
            continue
        else:
            tmp = ''
            while i < bibtex_str_len and bibtex_str[i] not in boundary_chars:
                tmp += bibtex_str[i]
                i += 1
            if tmp != '':
                token_stack.append(tmp)
        
    token_stack.reverse()
    return token_stack

def _bibtex_parse_s(bibtex_str):
    token_stack = bibtex_tokenize(bibtex_str)
    return _bibtex_parse_entry_list(token_stack)

def _bibtex_parse_entry_list(token_stack):
    ret = []
    while len(token_stack) > 0:
        ret.append(_bibtex_parse_entry(token_stack))
    return [x for x in ret if x]

def _bibtex_parse_entry(token_stack):
    global EXPAND
    if len(token_stack) < 4 or token_stack[-1] != '@':
        raise Exception("parse error, tokens={}".format(token_stack))  # TODO exception hierarchy
    token_stack.pop()   # @
    ret = {}
    ret['type'] = token_stack.pop().lower()
    if token_stack[-1] not in ('{', '('):
        raise Exception("parse error, expected { or (" + ", tokens={}".format(token_stack))
    token_stack.pop()   # {
    ret['fields'] = _bibtex_parse_field_list(token_stack)
    if '__cite_key' in ret['fields']:
        ret['cite_key'] = ret['fields']['__cite_key']
        del ret['fields']['__cite_key']
    token_stack.pop()   # }
    # Handle 'entry' which isn't - it's a string definition
    if ret['type'] == 'string':
        for field in ret['fields']:
            EXPAND[field] = ret['fields'][field]
        return {}
    return ret

def _bibtex_parse_field_list(token_stack):
    fields = {}
    # Parse first field
    field = _bibtex_parse_field(token_stack)
    # Handle cite key
    if field['value'] is None:
        fields['__cite_key'] = field['name']
    else:
        fields[field['name']] = field['value']
    # Handle remaining fields, none of which can be a cite key
    while token_stack[-1] == ',':
        token_stack.pop()
        field = _bibtex_parse_field(token_stack)
        fields[field['name']] = field['value']
    return fields

def _bibtex_parse_field(token_stack):
    ret = {}
    ret['name'] = token_stack.pop()
    if token_stack[-1] != ',':
        if token_stack[-1] != '=':
            raise Exception("parse error, expected '=', tokens={}, ret={}".format(token_stack, ret))
        token_stack.pop()   # =
        ret['value'] = _bibtex_parse_field_value(token_stack)
    else:
        ret['value'] = None
    return ret

def _bibtex_parse_field_value(token_stack):
    global EXPAND
    value = None
    if token_stack[-1] in ('"', '{'):
        token_stack.pop()   # opening delim
        value = token_stack.pop()
        token_stack.pop()   # closing delim
    else:
        value = ''
        # TODO handle months -> jun;
        while token_stack[-1] not in (',', '}', ')'):
            value += str(token_stack.pop())
            value += ' '
            
        # Handle string concatenation - TODO check semantics
        if '#' in value:
            parts = value.split('#')    # TODO split on regex r'\s*#\s*'
            tmp = parts[0].replace(' ', '').replace('\t', '')
            if tmp in EXPAND:
                value = EXPAND[tmp] + parts[1]
            else:
                tmp = parts[1].replace(' ', '').replace('\t', '')
                if tmp in EXPAND:
                    value = parts[0] + EXPAND[tmp]
        # Handle unquoted strings and integers
        elif not (set(value) - set(string.digits)):
            value = int(value)
    return value

