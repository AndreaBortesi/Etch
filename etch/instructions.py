from etch.api import MIXINS
from etch.utils import Instruction

class FunctionCallInstruction(Instruction):
    def __init__(self, interpreter, target, function, *args):
        self.interpreter = interpreter
        self.target = target
        self.function = function
        self.args = args
    def execute(self, context):
        if self.target:
            t = self.target.execute(context)
            try:
                return getattr(t, self.function)(*[i.execute(context) for i in self.args])
            except AttributeError:
                return MIXINS[t.__class__.__qualname__][self.function](t, *self.args)
        else:
            t = self.interpreter.__context__.vars
            return t[self.function](*[i.execute(context) for i in self.args])


class IfInstruction(Instruction):
    def __init__(self, interpreter, elif_, condition, ifTrue, ifFalse):
        self.interpreter = interpreter
        self.condition = condition
        print(condition)
        self.true = ifTrue
        self.false = ifFalse
        if elif_:
            self.elif_ = IfInstruction(interpreter, elif_[1:], interpreter.processInstruction(elif_[0][0]), interpreter.processStatements(elif_[0][1]), None)
        else:
            self.elif_ = None
    
    def execute(self, context):
        if self.condition.execute(context):
            for i in self.true:
                i.execute(context)
            return True
        elif self.elif_:
            if self.elif_.execute(context):
                return True
        if self.false:
            for i in self.false:
                i.execute(context)
            return False

class ForeverInstruction(Instruction):
    def __init__(self, interpreter, statements):
        self.statements = statements
    def execute(self, context):
        while True:
            for i in self.statements:
                i.execute(context)
class CountInstruction(Instruction):
    def __init__(self, interpreter, iterations, statements):
        self.iterations = iterations
        self.statements = statements
    def execute(self, context):
        for x in range(self.iterations.execute(context)):
            for i in self.statements:
                i.execute(context)
class WhileInstruction(Instruction):
    def __init__(self, interpreter, condition, statements):
        self.condition = condition
        self.statements = statements
    def execute(self, context):
        while self.condition.execute(context):
            for i in self.statements:
                i.execute(context)

class AssignInstruction(Instruction):
    def __init__(self, interpreter, name, value):
        self.name = name
        self.value = value
    def execute(self, context):
        context.setVar(self.name, self.value.execute(context))
class VariableReadInstruction(Instruction):
    def __init__(self, interpreter, name):
        self.name = name
    def execute(self, context):
        return context.getVar(self.name)
class SomecrementInstruction(Instruction):
    def __init__(self, interpreter, op, name):
        self.op = op
        self.name = name
    def execute(self, context):
        context.setVar(self.name, context.getVar(self.name) + 1)
class InPlaceModifyInstruction(Instruction):
    def __init__(self, interpreter, name, op, expr):
        self.name = name
        self.expr = expr
        self.op = op
    def execute(self, context):
        context.setVar(self.name, self.op(context.getVar(self.name), self.expr.execute(context)))        

BUILTINS = {
    "out": print,
    "get": input,
    "sum": sum,
    "min": min,
    "max": max
}