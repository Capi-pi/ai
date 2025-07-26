class Sentence:
    def evaluate(self, model):
        raise Exception("Nothing to evaluate")
    
    def formula(self):
        return ""
    
    def symbols(self):
        return set()
    
    @classmethod
    def validate(cls, sentence):
        if not isinstance(sentence, Sentence):
            raise TypeError ("Must be a logical sentence")
        
    @classmethod
    def parenthesize(cls, s):
        def balanced(s):
            count = 0
            for c in s:
                if c == "(":
                    count += 1
                elif c == ")":
                    if count <= 0:
                        return False
                    count -= 1
            return count == 0
        if not len(s) or s.isalpha() or (s[0] == "(" and s[-1] == ")" and balanced(s[1:-1])):
            return s
        else: 
            return f"({s})"

class Symbol(Sentence):
    def __init__(self, name):
        self.name = name
    
    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return NotImplemented
        return self.name == other.name
    
    def __hash__(self):
        return hash(("symbol", self.name))
    
    def __repr__(self):
        return f"{self.name}"
    
    def evaluate(self, model):
        if self.name in model:
            return model[self.name]
        else:
            raise Exception(f"Variable {self.name} not in model")
    
    def formula(self):
        return self.name
    
    def symbols(self):
        return {self.name}
    
class Not(Sentence):
    def __init__(self, operand):
        Sentence.validate(operand)
        self.operand = operand

    def __eq__(self, other):
        if not isinstance(other, Not):
            return NotImplemented
        return self.operand == other.operand
    
    def __hash__(self):
        return hash(("not", self.operand))
    
    def __repr__(self):
        return f"Not{self.operand}"
    
    def evaluate(self, model):
        return not self.operand.evaluate(model)
    
    def formula(self):
        return f"¬{Sentence.parenthesize(self.operand.formula())}"
    
    def symbols(self):
        return self.operand.symbols()
    
class And(Sentence):
    def __init__(self, *conjunctions):
        for conjuction in conjunctions:
            Sentence.validate(conjuction)
        self.conjunctions = list(conjunctions)
    
    def __eq__(self, other):
        if not isinstance(other, And):
            return NotImplemented
        return self.conjunctions == other.conjunctions
    
    def __hash__(self):
        return hash(("and", tuple(self.conjunctions)))
    
    def __repr__(self):
        return f"And({', ' .join(str(conjunction) for conjunction in self.conjunctions)})"
    
    def add(self, conjunction):
        Sentence.validate(conjunction)
        self.conjunctions.append(conjunction)
    
    def evaluate(self, model):
        return all(conjunction.evaluate(model) for conjunction in self.conjunctions)
    
    def formula(self):
        return " ∧ ".join(Sentence.parenthesize(conjunction.formula()) for conjunction in self.conjunctions)
    
    def symbols(self):
        result = set()
        for conjunction in self.conjunctions:
            result = result | conjunction.symbols()
        return result

class Or(Sentence):
    def __init__(self, *disjunctions):
        for disjunction in disjunctions:
            Sentence.validate(disjunction)
        self.disjunctions = list(disjunctions)
    
    def __eq__(self, other):
        if not isinstance(other, Or):
            return NotImplemented
        return self.disjunctions == other.disjunctions
    
    def __hash__(self):
        return hash(("or", tuple(self.disjunctions)))
    
    def __repr__(self):
        return f"Or({', ' .join(str(disjunction) for disjunction in self.disjunctions)})"
    
    def add(self, disjunction):
        Sentence.validate(disjunction)
        self.disjunctions.append(disjunction)
    
    def evaluate(self, model):
        for disjunction in self.disjunctions:
            if disjunction.evaluate(model) == True:
                return True
        return False
    
    def formula(self):
        return " ∨ ".join(Sentence.parenthesize(disjunction.formula()) for disjunction in self.disjunctions)
    
    def symbols(self):
        result = set()
        for disjunction in self.disjunctions:
            result = result | disjunction.symbols()
        return result
    
class Implication(Sentence):
    def __init__(self, antecedant, consequence):
        Sentence.validate(antecedant)
        Sentence.validate(consequence)
        self.antecedant = antecedant
        self.consequence = consequence
    
    def __eq__(self, other):
        if not isinstance(other, Implication):
            return NotImplemented
        return self.antecedant == other.antecedant and self.consequence == other.consequence
    
    def __hash__(self):
        return hash(("implication", (self.antecedant, self.consequence)))
    
    def __repr__(self):
        return f"Implication({', ' .join((str(self.antecedant), str(self.consequence)))})"
    
    def evaluate(self, model):
        return (not self.antecedant.evaluate(model)) or self.consequence.evaluate(model)
    
    def formula(self):
        return " => ".join((Sentence.parenthesize(self.antecedant.formula()), Sentence.parenthesize(self.consequence.formula())))

    def symbols(self):
        return set.union(self.antecedant.symbols(), self.consequence.symbols())

class Biconditional(Sentence):
    def __init__(self, left, right):
        Sentence.validate(left)
        Sentence.validate(right)
        self.left = left
        self.right = right

    def __eq__(self, other):
        return (isinstance(other, Biconditional)
                and self.left == other.left
                and self.right == other.right)

    def __hash__(self):
        return hash(("biconditional", hash(self.left), hash(self.right)))

    def __repr__(self):
        return f"Biconditional({self.left}, {self.right})"

    def evaluate(self, model):
        return ((self.left.evaluate(model)
                 and self.right.evaluate(model))
                or (not self.left.evaluate(model)
                    and not self.right.evaluate(model)))

    def formula(self):
        left = Sentence.parenthesize(str(self.left))
        right = Sentence.parenthesize(str(self.right))
        return f"{left} <=> {right}"

    def symbols(self):
        return set.union(self.left.symbols(), self.right.symbols())

    
def model_check(knowledge, query):
    """Checks if knowledge base entails query."""

    def check_all(knowledge, query, symbols, model):
        """Checks if knowledge base entails query, given a particular model."""

        # If model has an assignment for each symbol
        if not symbols:

            # If knowledge base is true in model, then query must also be true
            if knowledge.evaluate(model):
                return query.evaluate(model)
            return True
        else:

            # Choose one of the remaining unused symbols
            remaining = symbols.copy()
            p = remaining.pop()

            # Create a model where the symbol is true
            model_true = model.copy()
            model_true[p] = True

            # Create a model where the symbol is false
            model_false = model.copy()
            model_false[p] = False

            # Ensure entailment holds in both models
            return (check_all(knowledge, query, remaining, model_true) and
                    check_all(knowledge, query, remaining, model_false))

    # Get all symbols in both knowledge and query
    symbols = set.union(knowledge.symbols(), query.symbols())

    # Check that knowledge entails query
    return check_all(knowledge, query, symbols, dict())