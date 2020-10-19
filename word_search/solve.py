question_lines = []


def main():
    global question_lines
    question_file = open("question.text", "r")
    text = question_file.read()

    for t in text.split("\n"):
        tmp = []
        for i in t:
            tmp.append(i)
        if tmp:
            question_lines.append(tmp)

    products_file = open("products.text", "r")
    text = products_file.read()

    product_list = []

    for t in text.split("\n"):
        product_list.append(t)

    for t in product_list:
        for i in range(len(question_lines)):
            for j in range(len(question_lines[i])):
                # print(question_lines[i][j])
                if t[0] == question_lines[i][j]:
                    # print('==========')
                    for k in range(9):
                        if get_around(t[1:], i, j, k):
                            print(t, i, j, k)


def get_around(target, x, y, index):
    global question_lines
    if not target:
        return True
    try:
        if index == 0:
            return target[0] == question_lines[x - 1][y - 1] and get_around(
                target[1:], x - 1, y - 1, index
            )
        elif index == 1:
            return target[0] == question_lines[x - 1][y] and get_around(
                target[1:], x - 1, y, index
            )
        elif index == 2:
            return target[0] == question_lines[x - 1][y + 1] and get_around(
                target[1:], x - 1, y + 1, index
            )
        elif index == 3:
            return target[0] == question_lines[x][y - 1] and get_around(
                target[1:], x, y - 1, index
            )
        elif index == 4:
            return target[0] == question_lines[x][y] and get_around(
                target[1:], x, y, index
            )
        elif index == 5:
            return target[0] == question_lines[x][y + 1] and get_around(
                target[1:], x, y + 1, index
            )
        elif index == 6:
            return target[0] == question_lines[x + 1][y - 1] and get_around(
                target[1:], x + 1, y - 1, index
            )
        elif index == 7:
            return target[0] == question_lines[x + 1][y] and get_around(
                target[1:], x + 1, y, index
            )
        elif index == 8:
            return target[0] == question_lines[x + 1][y + 1] and get_around(
                target[1:], x + 1, y + 1, index
            )
    except IndexError:
        return False


if __name__ == "__main__":
    main()
