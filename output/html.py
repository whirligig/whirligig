#    Copyright (C) 2013 Denis Glushkov <denis@signal-mechanisms.com>
#
#    This file is part of Whirliglg.
#
#    Whirliglg is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Whirliglg is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Whirliglg.  If not, see <http://www.gnu.org/licenses/>.

#
# small html template rendering engine
#
import os
import re
import collections
import core
import _filters
import _globals

config = core.ConfigManager()
theme = config.get('theme')
config.done()

SEARCH_PATHS = (
    os.path.abspath(os.path.join(core.ROOT, 'themes', theme, 'templates/')),
    os.path.abspath(os.path.join(core.ROOT))
)

BOOL_FUNCTIONS = ('==', '!=', '>=', '<=', '>', '<', 'or', 'and')

#
# template error exception
#
class TemplateError(Exception):
    pass


#
# lexemes
#
class Text(object):

    def __init__(self, text):
        self.type = 'TEXT'
        self.text = text

    def __repr__(self):
        return "<Text:%s>" % self.text.__len__()

    def render(self, context, local_context={}):
        return self.text


class Filter(object):

    def __init__(self, name, value, *args):
        self.type = 'FILTER'
        self.name = name
        self.value = value
        self.args = args

    def __repr__(self):
        return "<Filter:%s>" % self.name

    def render(self, context, local_context={}):
        value = self.value.render(context, local_context)
        arg_values = map(lambda x: x.render(context, local_context), self.args)

        if self.name in _filters.filterCollection:
            return _filters.filterCollection[self.name](value, *arg_values)

        raise TemplateError('Undefined filter "%s"' % self.name)


class Boolean(object):

    def __init__(self, name, *args):
        self.name = name

    def __repr__(self):
        return "<Boolean:%s>" % self.name

    def render(self, context, local_context={}):
        return self.name


class Function(object):

    def __init__(self, name, *args):
        self.type = 'FUNCTION'
        self.name = name
        self.args = args

    def __repr__(self):
        return "<Function %s:%s>" % (
            self.name,
            map(lambda x: x.__repr__(), self.args)
        )

    def render(self, context, local_context={}):
        func = getattr(_globals, self.name, None)
        if func:
            args = map(lambda x: x.render(context, local_context), self.args)
            result = func(*args)
            try:
                result = func(*args)
            except:
                raise TemplateError('Unable get result from function "%s"' % self.name)
        else:
            result = ''
        return result


class Comment(object):

    def __init__(self, text):
        self.type = 'COMMENT'
        self.text = text

    def __repr__(self):
        return "<Comment:%s>" % self.text

    def render(self, context, local_context={}):
        return ''


class Variable(object):

    def __init__(self, name):
        self.type = 'VARIABLE'
        self.name = name
        parts = name.split('.')
        self.name = parts[0]
        self.keys = parts[1:] if parts.__len__() > 1 else []

    def __repr__(self):
        return "<Variable:%s>" % self.name

    def _check_int(self, s):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()

    def render(self, context, local_context={}):

        if self._check_int(self.name):
            return int(self.name)

        if self.name in local_context:
            value = local_context[self.name]
        elif self.name in context:
            value = context[self.name]
        else:
            raise TemplateError('Undefined variable "%s"' % self.name)

        if not self.keys or not value:
            return value

        try:
            i = iter(value)
            iterable = True
        except TypeError:
            iterable = False

        if not iterable:
            raise TemplateError('Variable "%s" is not iterable' % self.name)

        for key in self.keys:
            if self._check_int(key):
                key = int(key)

            if key in local_context and isinstance(local_context[key], collections.Hashable):
                value = value[local_context[key]]
            elif key in context and isinstance(context[key], collections.Hashable):
                value = value[context[key]]
            elif isinstance(key, str):
                value = value[key] if key in value else ''
            elif isinstance(key, int):
                value = value[key] if value and value.__len__() >= (key - 1) else ''
            # else:
            #     raise TemplateError('Undefined variable "%s[%s]"' % (self.name, key))

#            try:
#                value = value[key]
#            except KeyError:
#                raise TemplateError('Undefined variable "%s[%s]"' % (self.name, key))

        return value


class Tag(object):

    def __init__(self, name, *args):
        self.type = 'TAG'
        self.name = name
        self.args = args

    def __repr__(self):
        return "<Tag:%s (%s)>" % (
            self.name,
            ','.join(map(lambda x: str(x), self.args))
        )


class LoopTag(object):

    def __init__(self, *args):
        self.type = 'TAG'
        self.name = 'for'
        if args.__len__() != 3:
            raise TemplateError('Invalid syntax in "for"')
        self.current = args[0]
        self.key_in = args[1]
        self.iterable = args[2]
        self.content = []

    def __repr__(self):
        return "<Loop:%s>" % self.iterable

    def add_content(self, token):
        self.content.append(token)

    def render(self, context, _local_context={}):
        local_context = _local_context.copy()

        if self.key_in != 'in':
            raise TemplateError('Wrong syntax in "for"')

        # if isinstance(self.iterable, str):
        iterator = Expression(self.iterable).render(context, local_context)
        # else:
        #     result = self.iterable

        try:
            it = iter(iterator)
        except TypeError, msg:
            raise TemplateError(msg)

        result = ''

#        self.iterable = result
#        result = ''

        for loop, i in enumerate(iterator):
            local_context[self.current] = i
            local_context['loop'] = loop
            result += ''.join(str(token.render(context, local_context)) \
                for token in self.content)
        local_context = {}

        return result


class ConditionTag(object):

    def __init__(self, *args):
        self.type = 'TAG'
        self.name = 'if'
        self.content = []
        self.test = ' '.join(args)

    def __repr__(self):
        return "<Condition:%s>" % self.test

    def add_content(self, token):
        self.content.append(token)

    def render(self, context, local_context={}):
        result = Expression(self.test).render(context, local_context)
        if result and result not in ['None', '0', 'False']:
            return ''.join(str(token.render(context, local_context)) \
                for token in self.content)

        return ''


class Expression(object):
    '''
        Expressions are contains variables, filters, inclusion tags
        and bool functions: ==, !=, >=, <=, >, <
    '''

    def __init__(self, text):
        self.type = 'EXPRESSION'
        self.text = text

    def __repr__(self):
        return "<Expression:%s>" % self.text

    def parse(self):
        structure = []
        # split to args
        args = self.text.split()
        num_args = args.__len__()
        # check each arg for filter, inclusion tags
        for arg in args:

            # function
            m = re.match(r'^(\w+)\(([\w,\.\|\s\'\"]*?)\)$', arg)
            if m:
                if m.group(2):
                    args = map(lambda x: Expression(x), m.group(2).split(','))
                else:
                    args = []
                item = Function(m.group(1), *args)
                yield item
                continue

            # filters
            fls = re.findall(r'\|(\w+):?([\w,\'\"\(\)]*)', arg)
            if fls:
                item = Expression(arg.split('|')[0])
                for fl in fls:
                    if fl[1]:
                        args = map(lambda x: Expression(x), fl[1].split(':'))
                    else:
                        args = []
                    item = Filter(fl[0], item, *args)
                yield item
                continue

            # bool functions
            if arg in BOOL_FUNCTIONS:
                item = Boolean(arg)
                yield item
                continue

            # text
            if arg[0] == arg[-1] and arg[0] in ["'", '"']:
                item = Text(arg[1:-1])
                yield item
                continue

            # variable
            item = Variable(arg)
            yield item

    def render(self, context, local_context={}):
        args = []
        for item in self.parse():
            args.append( item.render(context, local_context) )

        if args.__len__() == 1:
            result = args[0]

        elif args.__len__() == 3 and args[1] in BOOL_FUNCTIONS:

            if isinstance(args[0], str):
                args[0] = '"%s"' % args[0]

            if isinstance(args[2], str):
                args[2] = '"%s"' % args[2]

            if isinstance(args[0], unicode):
                args[0] = 'u"%s"' % args[0]

            if isinstance(args[2], unicode):
                args[2] = 'u"%s"' % args[2]

            result = eval("%s %s %s" % (args[0], args[1], args[2]))

        else:
            result = args

        return result


tagCollection = {
    'if': ConditionTag,
    'for': LoopTag
}


#
# simple lexical analyzer
#
class Lexer(object):

    def __init__(self, text):
        self.text = text

    def logic_analyze(self):
        regexp = re.compile(r'(\{%.+?%\}|\{\{.+?\}\}|\{#.+?#\})')

        parts = regexp.split(self.text)

        for lexeme in parts:

            if lexeme.startswith('{%') and lexeme.endswith('%}'):
                # tag
                lexeme = lexeme[2:-2].strip()
                parts = lexeme.split()
                tag_name = parts[0]
                if parts.__len__() > 1:
                    args = parts[1:]
                else:
                    args = []
                if tag_name not in ('import', 'extends', 'include'):
                    yield Tag(tag_name, *args)
                continue

            if lexeme.startswith('{{') and lexeme.endswith('}}'):
                # expression
                lexeme = lexeme[2:-2].strip()
                yield Expression(lexeme)
                continue

            if lexeme.startswith('{#') and lexeme.endswith('#}'):
                # comment
                lexeme = lexeme[2:-2].strip()
                yield Comment(lexeme)
                continue

            if lexeme:
                yield Text(lexeme)

    def syntax_analyze(self):
        stack = []
        for lexeme in self.logic_analyze():
            if lexeme.type == 'TEXT':
                if stack:
                    stack[-1].add_content(lexeme)
                else:
                    yield lexeme
                continue

            if lexeme.type == 'TAG':
                tag = tagCollection.get(lexeme.name)
                if tag:
                    # enter to block
                    stack.append(tag(*lexeme.args))

                elif lexeme.name[:3] == 'end' and not stack:
                    raise TemplateError('Unbalanced "%s"' % lexeme.name)

                elif lexeme.name[:3] == 'end' and stack[-1].name == lexeme.name[3:]:
                    # end of block
                    current_block = stack.pop()
                    if not stack:
                        yield current_block
                    else:
                        stack[-1].add_content(current_block)

                elif lexeme.name[:3] == 'end' and stack[-1].name != lexeme.name[3:]:
                    raise TemplateError('Unbalanced "%s"' % lexeme.name)

                else:
                    raise TemplateError('Invalid tag "%s"' % (lexeme.name))
                continue

            if lexeme.type == 'EXPRESSION':
                if stack:
                    stack[-1].add_content(lexeme)
                else:
                    yield lexeme
                continue

            if lexeme.type == 'COMMENT':
                if stack:
                    stack[-1].add_content(lexeme)
                else:
                    yield lexeme
                continue


def _get_blocks(content):
    blocks = {}
    macros = []
    parent = ''

    matches = re.finditer(r'''
        \{%\s*block\s+(?P<name>\w+)\s*%\}(?P<block>.*?)\{%\s*endblock\s*%\}|
        \{%\s*extends\s+[\"\'](?P<extends>[\w\.\-\/\\]+?)[\"\']\s*%\}|
        \{%\s*include\s+[\"\'](?P<include>[\w\.\-\/\\]+?)[\"\']\s*%\}
        ''', content, (re.VERBOSE | re.DOTALL | re.MULTILINE))

    for m in matches:
        g = m.groupdict()
        if g['name'] and g['block']:
            blocks[g['name']] = g['block']

        if g['extends']:
            parent = g['extends']

    return (parent, blocks)


def _read_template(filename):
    for sp in SEARCH_PATHS:
        path = os.path.abspath(os.path.join(sp, filename))
        # security check
        if path.startswith(sp) and os.path.exists(path):
            with open(path, 'r+b') as fd:
                content = fd.read()
                parent, blocks = _get_blocks(content)

                if parent:
                    # get parent content and search blocks
                    content = _read_template(parent)
                    content = re.sub(r'\{%\s*block\s+(\w+)\s*%\}(.*?)\{%\s*endblock\s*%\}', \
                        lambda x: blocks[x.group(1)] if x.group(1) in blocks else '', content)
                    content = re.sub(r'\{%\s*include\s+[\"\']([\w\.\-\/\\]+?)[\"\']\s*%\}', \
                        lambda x: _read_template(x.group(1)), content)

            return content
    return ''


def template(filename, context, request):
    t = _read_template(filename)
    lexer = Lexer(t)

    result = ''

    context = dict(_globals.variableCollection.items() + context.items())
    context['request'] = request

    result = ''.join(str(token.render(context)) for token in lexer.syntax_analyze())
    return result