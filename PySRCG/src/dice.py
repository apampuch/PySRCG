from random import randint


def test_tn(dice, tn):
    successes = 0

    for roll in dice:
        if roll >= tn:
            successes += 1

    return successes


def roll_dice(num_dice: int, explode: bool = True):
    if num_dice <= 0:
        return 0

    print("Rolling {}d6...".format(num_dice))
    results = []

    for die in range(0, num_dice):
        total = 0
        cur_dice = randint(1, 6)
        total += cur_dice
        print(cur_dice)
        while cur_dice == 6 and explode is True:
            cur_dice = randint(1, 6)
            print(cur_dice)
            total += cur_dice

        print("")
        results.append(total)

    return results


if __name__ == "__main__":
    print(roll_dice(5))
