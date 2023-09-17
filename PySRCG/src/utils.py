import re

from copy import deepcopy
from operator import add, sub, mul, truediv
from tkinter import IntVar
from typing import Dict, List

from src.CharData.reportable import Reportable

DEBUG = False
STRINGS_THAT_ARE_NOT_VARIABLES = ["See", "rules", "yeah,", "right", "As", "weapon", "Special"]


def SET_DEBUG(val):
    global DEBUG
    DEBUG = val


def combine_tree_dict(dict1, dict2):
    # NYI
    final_dict = {}

    pass


def recursive_treeview_fill(_dict, parent_iid, treeview, recurse_check, recurse_end_callback, extra_keys=()):
    """
    Fill treeview recursively. Recursion stops when recurse_check returns false.
    recurse_check should take one argument, val, and return false when we don't want to recurse anymore.
    recurse_end_callback should take key, val, and iid as args, in that order, and return nothing.

    This should be called by libraries that are sorted by trees, like the list of items.

    :param _dict: The dictionary containing the data to fill from.
    :param parent_iid: Parent of the current iid.
        This is left blank on the orignal call. This variable changes on each recursion.
    :param treeview: The actual treeview object.
    :param recurse_check: The function we call to check if we need to continue recursing or not. Should return true if
        we should and false if we should stop recursion. USUALLY this should check for some value, like cybernetics
        should check if it has the "essence" value.
    :param recurse_end_callback: The function we call after all recursion is finished. This function will usually wrap
        the UI item we want to fill, usually a treeview, and set the passed in values to it.
    :param extra_keys: Extra keys to look for. This is used for treedicts with multiple columns, specifically in the
        Powers tab.
    """

    if DEBUG:
        pass  # breakpoint catcher

    for key in _dict.keys():
        val = _dict[key]

        # this dickery hackery is to make sure that multiple columns can be filled
        extra_vals = []
        for subkey in extra_keys:  # this should be blank most of the time
            if type(val) is dict and subkey in val.keys():  # validate input
                extra_vals.append(val[subkey])

        iid = treeview.insert(parent_iid, "end", text=key, values=extra_vals)

        if recurse_check(val):
            recursive_treeview_fill(val, iid, treeview, recurse_check, recurse_end_callback)
        else:
            recurse_end_callback(key, val, iid)


def treeview_get(treeview, helper_dict, make_copy=True):
    """Used by treeviews with a helper _dict for entries where only some are supposed to have functionality."""
    selection = treeview.selection()
    ret_val = None
    if type(helper_dict) is dict:
        if len(selection) == 0:
            ret_val = None
        selected_id = selection[-1]
        if selected_id in helper_dict.keys():
            ret_val = helper_dict[selected_id]
        else:
            ret_val = None
    elif type(helper_dict) is list:  # sometimes it's a list instead
        selected_index = treeview.index(selection)
        ret_val = helper_dict[selected_index]

    # return a copy if specified, otherwise return the direct value
    return deepcopy(ret_val) if make_copy else ret_val


"""
Variables in items and cyberware:
rating: Rating of the object
anything else: show a popup asking the value of X
be sure to search EVERYTHING for a variable and ask for it
some items like the data lock will probably require some field to call a specific function
"""


def get_variables(obj: Reportable, attributes):
    """
    Gets the variables from the expressions of the listed properties of an object,
    puts them in a dictionary, and returns it.
    :param obj: Object to get variables from.
    :param attributes: List of attributes to check for.
    :return: Dictionary with variable as key and IntVar set to 1 as value.
    """
    var_dict = {}

    # a list of optional attributes that can be ignored, like direct stat mods on cyberware
    optional_attributes = ["mods"]
    variable_match = r'^[a-zA-Z]'

    for attr in attributes:
        # do this if we have the attribute we're iterating through and if it's a string
        # this is probably just a simple expression
        if attr in obj.properties and type(obj.properties[attr]) is str:
            # split by spaces
            expression = obj.properties[attr]
            split_exp = expression.split()

            # look for anything that begins with a letter, that's a variable
            for substr in split_exp:
                match = re.match(variable_match, substr)
                # don't do it if it's in our strings to ignore
                if match and substr not in STRINGS_THAT_ARE_NOT_VARIABLES:
                    var_dict[substr] = IntVar()
                    var_dict[substr].set(1)

        # if it's a _dict, it should have only one key with another _dict as its values
        elif attr in obj.properties and type(obj.properties[attr]) is dict:
            tiered_dict = obj.properties[attr]

            # validate that it's key and values are valid
            keys = list(tiered_dict.keys())
            values = list(tiered_dict.values())
            if len(keys) != 1 or type(keys[0]) != str or type(values[0]) != dict:
                if attr in optional_attributes:
                    continue
                elif attr in obj.properties:
                    raise ValueError("Invalid setup for " + obj.name + ".")
                else:
                    raise ValueError("Invalid setup for nameless object.")

            var_dict[keys[0]] = IntVar()
            var_dict[keys[0]].set(1)

    return var_dict


def calculate_attributes(obj: Reportable, var_dict: Dict, attributes: List[str]):
    """
    Performs parse_arithmetic on obj for each attribute given in the list attributes if they exist on obj.
    Do this only if said property is a string or _dict.
    :param obj: The object to run calculations on.
    :param var_dict: The list of variables for parse_arithmetic to use.
    :param attributes: The list of attributes to check for on obj.
    """

    for attr in attributes:
        if attr in obj.properties:
            o = obj.properties[attr]
        else:
            continue

        if type(o) is str:
            result = parse_arithmetic(o, var_dict)
            obj.properties[attr] = result

        # do this if we have the attribute and if it's a dict and if it's not empty
        # this is probably one of those stupid things where the cost multipliers are "tiered"
        # e.g. rating 1-4 costs rating * 1000; rating 5-7 costs rating * 2000
        # in this case it'll be formatted as "rating 1-4:rating*1000"
        elif type(o) is dict and len(o.keys()) > 0:
            # the "root node" of the tiered variable (as I'm now calling them) should be a string that refers to
            # another attribute in the object that's already been solved, get it,
            # and throw an error if we can't find it
            tiered_dict_root = o

            # validate that it's key and values are valid
            keys: List[str] = list(tiered_dict_root.keys())
            values: List[dict] = list(tiered_dict_root.values())

            not_one_root = len(keys) != 1              # there should only be one root value
            root_not_string = type(keys[0]) != str      # root value should be a string
            value_not_dict = type(values[0]) != dict    # value should be a _dict
            if not_one_root or root_not_string or value_not_dict:
                # if the attribute we're looking at is "mods" and the thing isn't valid, we need to do something special
                if attr == "mods":
                    obj.properties[attr] = calculate_mods(tiered_dict_root, var_dict, obj.properties["name"])
                    continue
                elif "name" in obj.properties:
                    raise ValueError("Invalid setup for " + obj.name + ".")
                else:
                    raise ValueError("Invalid setup for nameless object.")

            # the children of the root node should be "key value pairs", where the "key" is a statement as a
            # specifically-formatted string that represents a statement that can be evaluated to true or false
            # e.g. "x <= 4"
            # find the one that matches, then calculate the attribute that's the value of that "key"
            # if there's no matching key then throw an error
            variable: str = keys[0]
            if variable in var_dict:
                result = parse_between_expression(var_dict, var_dict[variable], values[0])
                obj.properties[attr] = result

            else:
                if "name" in obj.properties:
                    raise ValueError("Key " + variable + " not in " + obj.name + ".")
                else:
                    raise ValueError("Key " + variable + " not in nameless object.")


def calculate_mods(mods_dict, var_dict, name="NAMELESS"):
    for key in mods_dict.keys():
        val = mods_dict[key]
        if type(val) is str:
            mods_dict[key] = parse_arithmetic(val, var_dict)
        elif type(val) is dict:
            # blah blah blah DRY principle, whatever

            # validate that it's key and values are valid
            keys: List[str] = list(val.keys())
            values: List[dict] = list(val.values())

            not_one_root = len(keys) != 1              # there should only be one root value
            root_not_string = type(keys[0]) != str      # root value should be a string
            value_not_dict = type(values[0]) != dict    # value should be a _dict
            if not_one_root or root_not_string or value_not_dict:
                # if the attribute we're looking at is "mods" and the thing isn't valid, we need to do something special
                raise ValueError(f"Invalid setup for mods dict for {name}.")

            # the children of the root node should be "key value pairs", where the "key" is a statement as a
            # specifically-formatted string that represents a statement that can be evaluated to true or false
            # e.g. "x <= 4"
            # find the one that matches, then calculate the attribute that's the value of that "key"
            # if there's no matching key then throw an error
            variable: str = keys[0]
            if variable in var_dict:
                result = parse_between_expression(var_dict, var_dict[variable], values[0])
                mods_dict[key] = result
        else:
            raise ValueError("Mods dict is not working.")

    return mods_dict


def parse_between_expression(var_dict, variable, expression_dict):
    """
    Takes an integer variable and a string:string expression_dict. The key string is a semicolon-separated expression
    denoting the lower and upper bounds of the value it can match, while the value string is a simple arithmetic
    expression that can be parsed via parse_arithmetic. It will find the expression where the value of variable is
    between X;Y, execute that expression, and return the result. ValueError will be thrown if no suitable expression is
    found.
    :type var_dict: dict
    :type expression_dict: dict
    :type variable: int
    :param var_dict: Variable dictionary for parse_arithmetic.
    :param variable: Variable to find the
    :param expression_dict:
    :return: result of the expression.
    """

    # iterate to find the key we're using
    use_key = None
    for key in expression_dict.keys():
        # split and format to int
        split_expression = key.split(";")
        if "" in split_expression:
            split_expression.remove("")
        split_expression = list(map(int, split_expression))

        matches = False
        # if the last character is a semicolon, just check if greater than or equal to
        if key[-1] == ";":
            matches = variable >= split_expression[0]
        # if the first character is a semicolon, just check if lesser than or equal to
        elif key[0] == ";":
            matches = variable <= split_expression[0]
        # otherwise, check if between
        else:
            matches = split_expression[0] <= variable <= split_expression[1]

        if matches:
            use_key = key
            break

    if use_key is None:
        raise ValueError("No matching expression found!")

    # return the result of the statement matching the key we found
    # it should only parse if it's an expression (string), otherwise just return the value
    expression = expression_dict[use_key]
    if type(expression) is int or type(expression) is float:
        return expression
    elif type(expression) is str:
        try:
            return parse_arithmetic(expression, var_dict)
        # if it's not able to be parsed, assume we should just return it as-is
        except ValueError:
            return expression
        # if the expression has a variable that can't be filled, assume we should just return it as-is
        except KeyError:
            return expression
    elif type(expression) is dict:
        # If the type of the "expression" is a _dict, we're probably dealing with mods for things like attributes.
        # In that case, we need to parse the expression in each child
        for key in expression.keys():
            if type(expression[key]) is str:
                expression[key] = parse_arithmetic(expression[key], var_dict)

        return expression
    else:
        raise TypeError(f"Invalid type for expression {expression}")


def parse_arithmetic(expression, var_dict):
    """
    set current fork as root
    for each operation N
        scan left to right until we hit a tier N operation
        split by that operation
        replace current fork with split operation
        put sides on tree
        remove leading/trailing whitespace on both sides
        replace current fork with right side
        continue scan on right side, repeating above steps with current fork

        recurse with this operator for children

    do the calculation

    if you get an error anywhere it's probably due to an invalid expression
    """
    operators = (r'[\+\-]', r'[\*\/]')  # regex for * / + -
    root = AstNode(expression)

    # iterate through everything separated by whitespace, creating an abstract syntax tree
    for opset in operators:
        parse_branch(root, opset)
    set_modes(root)

    # print("##################")

    final = run_calc(root, var_dict)
    if DEBUG:
        print(final)
    return final


def parse_branch(node, ops):
    exp = node.symbol  # expression

    search = re.search(ops, exp)
    if search:
        node.symbol = re.findall(ops, exp)[-1]  # set the symbol to the LAST thing we matched with
        # print("Operator: " + node.symbol)
        child_strs = backwards_re_split(ops, exp)
        # child_strip = []  # debugging thing only

        # make a node for each child
        for child in child_strs:
            # child_strip.append(child.strip())
            node.children.append(AstNode(child.strip()))
        # print(child_strip)

    # recursively do the above for each child
    for child in node.children:
        parse_branch(child, ops)


def set_modes(node):
    if len(node.children) > 0:
        for child in node.children:
            set_modes(child)

    if re.search(r'\d', node.symbol):  # check if matching a number
        node.mode = "NUM"
    elif re.search(r'[+\-*/]', node.symbol):  # check if matching an operator
        node.mode = "OP"
    else:
        node.mode = "VAR"

    # print("SYM: " + node.symbol + " MODE: " + node.mode)


def run_calc(node, _vars):
    if node.mode == "OP":
        # figure out the operation
        operation = None
        if node.symbol == "+":
            operation = add
        elif node.symbol == "-":
            operation = sub
        elif node.symbol == "*":
            operation = mul
        elif node.symbol == "/":
            operation = truediv
        else:
            raise ValueError("OP symbol is not +, -, *, or /.")
        # there should always only be two children
        a = run_calc(node.children[0], _vars)
        b = run_calc(node.children[1], _vars)
        return operation(a, b)
    elif node.mode == "NUM":
        # convert to number and return
        return float(node.symbol)
    elif node.mode == "VAR":
        return _vars[node.symbol]
    else:
        raise ValueError("Invalid expression.")


def backwards_re_split(split_regex, phrase):
    """This exists because re.split() only splits counting from the left.
    This makes it split starting from the right."""
    # reverse the phrase
    phrase = phrase[::-1]
    phrase = re.split(split_regex, phrase, 1)
    phrase = phrase[::-1]
    for i in range(0, len(phrase)):
        phrase[i] = phrase[i][::-1]

    return phrase


def magic_tab_show_on_awakened_status(app_data):
    """Hides or shows the magic tab based on whether the character is awakened or not.
    :type app_data: app_data
    """
    if app_data.app_character.statblock.awakened is None:
        app_data.window.tab(".!app.!magictab", state="hidden")
    else:
        app_data.window.tab(".!app.!magictab", state="normal")


class AstNode:
    def __init__(self, symbol):
        self.symbol = symbol
        self.children = []
        self.mode = None  # is None, "OP", "NUM", or "VAR"


if __name__ == "__main__":
    DEBUG = True

    variable_dict = {"rating": 993}

    parse_arithmetic("2+5", variable_dict)  # 993
