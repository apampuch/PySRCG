"""
This is global data for the whole program.
"""
from src.adjustment import AdjustmentsContainer

top_bar = None  # should be the top bar
root = None  # should be the window for the program
window = None  # should be the main notebook
# WHY THE FUCK IS THIS A STRING??? it becomes a Character but still wtf
app_character = "None"  # should be a Character()

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

