"""
This is global data for the whole program.
"""
from src.adjustment import AdjustmentsContainer

top_bar = None  # should be the top bar
root = None  # should be the window for the program
window = None  # should be the main notebook
menu = None # should be the menu
# WHY THE FUCK IS THIS A STRING??? it becomes a Character but still wtf
app_character = "None"  # should be a Character()

# all of the top level tabs, set automatically on launch, DO NOT CHANGE
setup_tab = None
attributes_tab = None
background_tab = None
skills_tab = None
gear_tab = None
magic_tab = None
augments_tab = None
decking_tab = None
rigging_tab = None
karma_tab = None

cash_update_events = []
tab_switch_events = []

# THESE ARE NOT SAVED
# adjustments_list = AdjustmentsContainer()


def on_cash_updated():
    for event in cash_update_events:
        event()


def on_tab_switched():
    for event in tab_switch_events:
        event()


def pay_cash(amount, *args):
    """This exists so we can update the global cash counter.
    :param amount: Amount to pay
    :type args: bool[]
    """

    paid = app_character.statblock.pay_cash(amount, *args)

    return paid

