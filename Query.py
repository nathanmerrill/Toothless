from pyparsing import ParseException
import string
import random

class Query:
    def __init__(self):
        self.inputs = set()
        self.outputs = []
        self.admin_command = False
        self.hash_code = 0
        self.is_important = False

    def is_admin(self):
        self.admin_command = True
        return self

    def add_input(self, inp):
        self.inputs.add(" "+inp+" ")
        self.hash_code += 13*hash(inp)
        return self

    def add_inputs(self, inputs):
        for inp in inputs:
            self.add_input(inp)
        return self

    def add_output(self, output):
        self.outputs.append(output)
        self.hash_code += 7*hash(output)
        return self

    def add_outputs(self, outputs):
        self.outputs.extend(outputs)
        return self

    def add_string_output(self, output):
        self.add_output(lambda *args: output)
        return self

    def add_string_outputs(self, outputs):
        for output in outputs:
            self.add_string_output(output)
        return self

    def make_important(self):
        self.is_important = True
        return self

    def matches(self, message, user):
        orig = message
        message = " "+message.lower()+" "
        exclude = set(string.punctuation)
        message = ''.join(ch for ch in message if ch not in exclude and ch is not "/")
        for inp in self.inputs:
            if inp in message:
                if self.admin_command:
                    priority = 500 if user.is_admin else 0
                else:
                    priority = 250 if self.is_important else len(inp)
                return priority, Response(self.outputs, get_postfix(orig, inp),self.hash_code)
        return 0, None


class Response:
    def __init__(self, outputs=None, postfix="", unique_id=0):
        self.outputs = outputs if outputs else [lambda *args: "meep"]
        self.postfix = postfix
        self.id = unique_id

    def respond(self, user):
        output = self.outputs[min((int(user.calculate_favor()*len(self.outputs)/100.0)), len(self.outputs)-1)]
        try:
            response = output(self.postfix, user)
        except (ParseException, ZeroDivisionError, IndexError, OverflowError, ValueError):
            pass
            return "Bad command"
        response = inject_variables(response, user, self.postfix)
        user.add_favor(self.id)
        return response


def get_postfix(full, prefix):
    if prefix in full.lower():
        index = full.lower().index(prefix)+len(prefix)
        return full[index:]
    else:
        return full


def inject_variables(message, user, sub_string):
    if "$" not in str(message):
        return message
    return message.replace("$substring", sub_string)\
        .replace("$username", user.name)\
        .replace("$userfavor", str(user.favor))
