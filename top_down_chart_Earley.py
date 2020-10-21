# 清华大学计算语言学(孙茂松老师)作业: 语法分析
# Top-down Chart算法（Earley算法）（参考Allen 1995 Natural Language Understanding 3.6节）
# by Mimicry Hu

class Arc:
    def __init__(self, rule, start, end, constituents):
        self.rule = rule
        self.start = start
        self.end = end
        self.constituents = constituents
        self.state = "active"
        self.matched = []

    def output(self):
        constituents = "&".join(self.constituents)
        return "arc," + str(self.rule) + ',' + str(self.start) + ',' + str(self.end) + ',' + constituents + ','


class Constituent:
    def __init__(self, symbol, start, end, id, rule, constituents):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.id = id
        self.rule = rule
        self.constituents = constituents

    def output(self):
        if self.rule is not None:
            rule = str(self.rule)
        else:
            rule = ""
        constituents = "&".join(self.constituents)
        return "constituent," + self.symbol + ',' + str(self.start) + ',' + str(self.end) + ',' + str(self.id) + ',' \
               + rule + ',' + constituents + ','


input_str = "the large can can hold the water"
# input_str = "老 张 在 编辑 操作 手册"

rules = [["S", "NP", "VP"],
         ["NP", "ART", "ADJ", "N"],
         ["NP", "ART", "N"],
         ["NP", "ADJ", "N"],
         ["VP", "AUX", "VP"],
         ["VP", "V", "NP"]]

# rules = [["S", "NP", "VP"],
#          ["NP", "N"],
#          ["NP", "ADJ", "SURNAME"],
#          ["NP", "N", "N"],
#          ["NP", "V", "N"],
#          ["NP", "ADJ", "N"],
#          ["PP", "PREP", "NP"],
#          ["VP", "V"],
#          ["VP", "V", "NP"],
#          ["VP", "ADV", "V"],
#          ["VP", "PP", "VP"]]

lexicon = {
    "the": ["ART"],
    "large": ["ADJ"],
    "can": ["N", "AUX", "V"],
    "hold": ["N", "V"],
    "water": ["N", "V"]
}

# lexicon = {
#     "老": ["ADJ", "ADV"],
#     "张": ["SURNAME", "V"],
#     "在": ["V", "ADV", "PREP"],
#     "编辑": ["N", "V"],
#     "操作": ["N", "V"],
#     "手册": ["N"]
# }

terminal_symbols = ["ART", "ADJ", "ADV", "N", "AUX", "V", "SURNAME", "PREP"]

word_list = input_str.split(' ')

agenda = [Arc(1, 1, 1, [])]
print(agenda[0].output())
cons_stack = []
cons_id = 1


def arc_extension(cons):
    for arc in agenda:
        if arc.state == "active" or arc.state == "rewritten" or arc.state == "succeeded_0":
            if cons.start == arc.end and \
                    cons.symbol == rules[arc.rule - 1][len(arc.constituents) + 1]:
                if len(arc.constituents) + 2 == len(rules[arc.rule - 1]):
                    if str(cons.id) not in arc.matched:
                        sub_cons = arc.constituents
                        sub_cons.append(str(cons.id))
                        global cons_id
                        new_cons = Constituent(rules[arc.rule - 1][0], arc.start, cons.end,
                                               cons_id, arc.rule, sub_cons)
                        cons_id += 1
                        cons_stack.append(new_cons)
                        print(new_cons.output())
                        if rules[arc.rule - 1][len(arc.constituents)] in terminal_symbols:
                            arc.state = "succeeded"
                        else:
                            arc.matched.append(arc.constituents.pop())
                            arc.state = "succeeded_0"
                        # return


def arc_introduction(arc, pos, used_rules):
    for index, r in enumerate(rules):
        if arc.end >= pos:
            if arc.state == 'active' or arc.state == "rewritten":
                cur_pos = arc.end
                if r[0] == rules[arc.rule - 1][len(arc.constituents) + 1]:
                    if index + 1 not in used_rules:
                        new_arc = Arc(index + 1, cur_pos, cur_pos, [])
                        print(new_arc.output())
                        agenda.append(new_arc)
                        arc.state = "rewritten"
                        used_rules.append(index + 1)
                        # return


for position, word in enumerate(word_list):
    # arc introduction (rewrite)
    used_rules = []
    for arc in agenda:
        arc_introduction(arc, position + 1, used_rules)

    # add the next lexical symbol
    for s in lexicon[word]:
        c = Constituent(s, position + 1, position + 2, cons_id, None, [])
        cons_id += 1
        cons_stack.append(c)
        print(c.output())

    # extend all the arcs
    for cons in cons_stack:
        arc_extension(cons)

    # arc introduction
    arc_num = len(agenda)
    for i in range(arc_num):
        arc_i = agenda[i]
        if arc_i.state == "active" or arc_i.state == "rewritten":
            for cons in cons_stack:
                if cons.start == arc_i.end and cons.symbol == rules[arc_i.rule - 1][len(arc_i.constituents) + 1]:
                    arc_i.state = "extended"
                    cons_list = arc_i.constituents
                    cons_list.append(str(cons.id))
                    new_arc = Arc(arc_i.rule, arc_i.start, cons.end, cons_list)
                    arc_i.constituents = []
                    agenda.append(new_arc)
                    print(new_arc.output())
            if arc_i.state != "extended" and rules[arc_i.rule - 1][len(arc_i.constituents) + 1] in terminal_symbols:
                arc_i.state = "failed"

    # remove used constituents
    cons_stack = []


