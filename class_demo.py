

class person:
    def __init__(self, name, height, weight):
        self.name = name
        self.height = height
        self.weight = weight


def find_weightest_person(persons):
    weightest_person = persons[0]
    for person in persons:
        if person.weight > weightest_person.weight:
            weightest_person = person
    return weightest_person


def find_hightest_person(persons):
    hightest_person = persons[0]
    for person in persons:
        if person.height > hightest_person.height:
            hightest_person = person
    return hightest_person


if __name__ == '__main__':
    # wangsixue 142 30
# zhaominghao 140 32
# zhangsan 150 30
# lisi 140 30
# wangwu 140 30
    persons = [person('wangsixue', 142, 30), person('zhaominghao', 140, 32), person('zhangsan', 150, 30), person('lisi', 140, 30), person('wangwu', 140, 30)]
    weightest_person = find_weightest_person(persons)
    hightest_person = find_hightest_person(persons)
    print('The weightest person is:', weightest_person.name)
    print('The hightest person is:', hightest_person.name)