import argparse as ap

import re

import platform

import copy


class Candidade:
    def __init__(self, name: string, ):
        return


def graphsearch(map, flag):
    def distance_G(node1, node2):
        x1 = abs(node1.x - node2.x)
        y1 = abs(node1.y - node2.y)
        if x1 == 1 and y1 == 0:
            return 2
        if x1 == 0 and y1 == 1:
            return 2
        if x1 == 1 and y1 == 1:
            return 1
        else:
            return 0

    class Node:
        def __init__(self, x, y, identifier, operator, end_x, end_y, parent=None):
            self.x = x
            self.y = y
            self.identifier = identifier
            self.parent = parent
            if parent != None:
                G_to_parent = distance_G(self, parent)
                self.g = G_to_parent + parent.g
                self.operator = parent.operator + "-" + operator
                self.last_operator = operator
            else:
                self.g = 0
                self.operator = operator
                self.last_operator = ""

            self.h = min(abs(end_x - self.x), abs(end_y - self.y)) + abs(abs(end_x - self.x) - abs(end_y - self.y)) * 2
            self.f = self.h + self.g
            self.children = []
            self.order_of_expansion = None

        def __str__(self):
            return "%s: %s" % (self.identifier, self.operator)

    def getOperator(offset_x, offset_y):
        operators = {
            '1,0': 'R', '1,1': 'RD', '0,1': 'D', '-1,1': 'LD', '-1,0': 'L', '-1,-1': 'LU', '0,-1': 'U', '1,-1': 'RU'
        }
        return operators[str(offset_x) + ',' + str(offset_y)]

    def identifier_generator():
        counter = 0
        while True:
            yield 'N' + str(counter)
            counter += 1

    identifier = identifier_generator()

    map = [i.strip() for i in map]
    size = int(map[0])
    map = map[1:]
    if size != len(map):
        print("Error: This input file is not in right format!")
        return -1
    # convert into Array2D
    map = [list(i) for i in map]
    # copy a map for later using.
    copymap = map.copy()

    openList = []
    closeList = []
    # x,y of Start point
    S_x = 0
    S_y = 0
    # end point x and y
    end_x = 0
    end_y = 0
    for i in range(len(map)):
        for j in range(len(map)):
            if map[i][j] == "S":
                S_x = j
                S_y = i
            if map[i][j] == "G":
                end_x = j
                end_y = i
    startNode = Node(S_x, S_y, next(identifier), 'S', end_x, end_y)
    openList.append(startNode)

    # Tie-breaking rules
    # the first node with minimum f score among nodes in openList will be selected as next one, when there several nodes have same minimum f score.
    def getMinNode():
        currentNode = openList[0]
        for node in openList:
            if node.f < currentNode.f:
                currentNode = node
        return currentNode

    def generateChildren(node):
        for offset_y in range(-1, 2):
            for offset_x in range(-1, 2):
                child_x = node.x + offset_x
                child_y = node.y + offset_y
                # exclude itself
                if offset_y == 0 and offset_x == 0:
                    continue
                # exclude node outside the map
                if child_x not in range(len(map)) or child_y not in range(len(map)):
                    continue
                # exclude the mountainous tile node
                if map[child_y][child_x] == 'X':
                    continue
                # exclude the diagonal node where one of the directions of it parent node composing the diagonal contains a mountainous tile
                if offset_y * offset_x != 0 and (map[child_y][node.x] == 'X' or map[node.y][child_x] == 'X'):
                    continue
                operator = getOperator(offset_x, offset_y)
                child_node = Node(child_x, child_y, next(identifier), operator, end_x, end_y, parent=node)
                #                 child.order_of_expansion = node.operator + " " + child.operator

                node.children.append(child_node)
        return node.children

    def nodeInCloseList(node):
        for oldNode in closeList:
            if oldNode.x == node.x and oldNode.y == node.y:
                return True
        return False

    def nodeInOpenList(node):
        for oldNode in openList:
            if oldNode.x == node.x and oldNode.y == node.y:
                return oldNode
        return None

    def endNodeInCloseList():
        for node in openList:
            if node.h == 0:
                return node
        return None

    def diagnose(node):
        print(str(node) + " ")

    def print_node_info(node):
        print(str(node) + " " + " ".join(
            [str(node.last_operator), str(node.order_of_expansion), str(node.g), str(node.h), str(node.f)]))
        print("Children: {" + ", ".join([str(child) + " " + str(child.last_operator) for child in node.children]) + "}")
        print("OPEN: {" + ", ".join(
            ["(" + str(i) + " " + str(i.last_operator) + " " + " ".join([str(i.g), str(i.h), str(i.f)]) \
             + ")" for i in openList]) + "}")
        print("CLOSED: {" + ", ".join(
            ["(" + str(i.identifier) + ": " + str(i.last_operator) + " " + " ".join([str(i.order_of_expansion), \
                                                                                     str(i.g), str(i.h),
                                                                                     str(i.f)]) + ")" for i in
             closeList]) + "}")
        print("\n")

    notFinished = True
    solution = ""
    order = 1
    f = flag
    while openList and notFinished:
        # find node with min f value
        minNode = getMinNode()
        minNode.order_of_expansion = order
        order += 1
        # remove it from OPEN and add it into CLOSE
        closeList.append(minNode)
        openList.remove(minNode)
        # ready to add child into openList
        children = generateChildren(minNode)
        for child in children:
            # if child in closelist, just ignore
            if nodeInCloseList(child):
                continue
            oldNode = nodeInOpenList(child)
            # if child not in openlist,add it into openlist
            if not oldNode:
                openList.append(child)
            else:
                # if child has less g value than oldNode, replace it.
                # Tie-breaking rules
                # when old node which is already in openList and new node which is ready to put into openList have same g score,
                # the old node will be remained in openList and the new node will be ignored.
                if child.g < oldNode.g:
                    openList.remove(oldNode)
                    openList.append(child)
        if flag > 0:
            print_node_info(minNode)
            flag -= 1
        endNode = endNodeInCloseList()
        # if endNode in openList, then searching ends
        if endNode:
            notFinished = False
            current = endNode
            path = ["G"]
            cost = []
            mapList = []
            while current:
                output_map = copy.deepcopy(copymap)
                path.append("-")
                path.append(current.last_operator)
                cost.append(current.g)
                if current.x != end_x or current.y != end_y:
                    output_map[current.y][current.x] = "*"
                for j in range(len(output_map)):
                    output_map[j] = "".join(output_map[j]) + "\n"
                output_map = "".join(output_map) + "\n"
                mapList.append(output_map)
                current = current.parent
            for i in range(len(cost) - 1, -1, -1):
                solution += mapList[i]
                solution += "".join(path[i * 2:][::-1])
                solution += ("  " + str(cost[i]) + "\n\n")

    # For diagnostic mode

    return solution


def read_from_file(file_name):
    file_handle = open(file_name)

    map = file_handle.readlines()

    return map


def write_to_file(file_name, solution):
    file_handle = open(file_name, 'w')

    file_handle.write(solution)


def main():
    # create a parser object

    parser = ap.ArgumentParser()

    # specify what arguments will be coming from the terminal/commandline

    parser.add_argument("input_file_name", help="specifies the name of the input file", type=str)

    parser.add_argument("output_file_name", help="specifies the name of the output file", type=str)

    parser.add_argument("flag", help="specifies the number of steps that should be printed", type=int)

    # parser.add_argument("procedure_name", help="specifies the type of algorithm to be applied, can be D, A", type=str)

    # get all the arguments

    arguments = parser.parse_args()

    ##############################################################################

    # these print statements are here to check if the arguments are correct.

    #    print("The input_file_name is " + arguments.input_file_name)

    #    print("The output_file_name is " + arguments.output_file_name)

    #    print("The flag is " + str(arguments.flag))

    #    print("The procedure_name is " + arguments.procedure_name)

    ##############################################################################

    # Extract the required arguments

    operating_system = platform.system()

    if operating_system == "Windows":

        input_file_name = arguments.input_file_name

        input_tokens = input_file_name.split("\\")

        if not re.match(r"(INPUT\\input)(\d)(.txt)", input_file_name):
            print("Error: input path should be of the format INPUT\input#.txt")

            return -1

        output_file_name = arguments.output_file_name

        output_tokens = output_file_name.split("\\")

        if not re.match(r"(OUTPUT\\output)(\d)(.txt)", output_file_name):
            print("Error: output path should be of the format OUTPUT\output#.txt")

            return -1

    else:

        input_file_name = arguments.input_file_name

        input_tokens = input_file_name.split("/")

        if not re.match(r"(INPUT/input)(\d)(.txt)", input_file_name):
            print("Error: input path should be of the format INPUT/input#.txt")

            return -1

        output_file_name = arguments.output_file_name

        output_tokens = output_file_name.split("/")

        if not re.match(r"(OUTPUT/output)(\d)(.txt)", output_file_name):
            print("Error: output path should be of the format OUTPUT/output#.txt")

            return -1

    flag = arguments.flag

    # procedure_name = arguments.procedure_name

    try:

        map = read_from_file(input_file_name)  # get the map

    except FileNotFoundError:

        print("input file is not present")

        return -1

    # print(map)

    solution_string = ""  # contains solution

    solution_string = graphsearch(map, flag)

    write_flag = 1

    # call function write to file only in case we have a solution

    if write_flag == 1:
        write_to_file(output_file_name, solution_string)


if __name__ == "__main__":
    main()

