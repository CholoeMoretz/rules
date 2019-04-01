# 基于依存句法的规则
import re
from pyltp import Segmentor, Postagger, Parser


TRIGGER_WORDS = ["导致", "引起", "使得", "造成", "引发", "招致", "致使"]


# 去掉因果短语开头及结尾的多余成分
_post_process_pattern = re.compile(r"^(-|、|的|和|以及)*(.+?)(-|、|的|和|以及)*$")
def _post_process(phrase):
    m = _post_process_pattern.search(phrase)
    if m:
        return m.group(2)
    return phrase


# 输出格式：抽取规则\t\t\t时间戳\t\t\t原因短语 触发词 结果短语\t\t\t上下文
def format_output(rule, time, context, phrase_list):
    processed_list = []
    for phrase in phrase_list:
        processed_list.append(_post_process(phrase))
    return rule + "\t\t\t" + time + "\t\t\t" + (" ".join(processed_list)) + "\t\t\t" + context


class DependencyTreeNode:
    def __init__(self, text, position, relation):
        self.text = text
        self.relation = relation
        self.position = position
        self.children = []
        self.parent = None

    def print(self, indent = ""):
        print(indent + str(self.position) + ":" + self.text + ":" + self.relation)
        for child in self.children:
            child.print(indent + "  ")

    def traverse(self, func):
        func(self)
        for child in self.children:
            child.traverse(func)

    def find(self, cond_func):
        if cond_func(self):
            return self
        for child in self.children:
            result = child.find(cond_func)
            if result:
                return result
        return None


def build_dependency_tree(sentence, segmentor, postagger, parser):
    words = segmentor.segment(sentence)
    postags = postagger.postag(words)
    arcs = parser.parse(words, postags)

    nodes = []
    for i in range(0, len(words)):
        nodes.append(DependencyTreeNode(words[i], i + 1, arcs[i].relation))
    root = DependencyTreeNode("ROOT", 0, "")
    for i in range(0, len(words)):
        parent_position = arcs[i].head
        if parent_position == 0:
            nodes[i].parent = root
            root.children.append(nodes[i])
        else:
            parent_position = parent_position - 1
            nodes[i].parent = nodes[parent_position]
            nodes[parent_position].children.append(nodes[i])
    return root


# 每条规则返回: (is_done, cause, effect)
# is_done: 是否还需要后续规则再处理
# cause: 原因
# effect: 结果
# connective: 连接词

# A造成B句式
def rule_1(connective_node, remove_word_dict):
    is_done = False
    cause = None
    effect = None
    connective = None

    sbv_list = []
    vob_list = []

    for child in connective_node.children:
        if child.relation == "SBV":
            sbv_list.append(child)
        elif child.relation == "VOB" or child.relation == "DBL":
            vob_list.append(child)
        elif child.relation == "ADV" and child.text in ["因", "因为", "由", "由于"]:
            for grand_child in child.children:
                if grand_child.relation == "POB":
                    sbv_list.append(grand_child)

    if len(sbv_list) > 0 and len(vob_list) > 0:
        cause_list = []
        for sbv in sbv_list:
            sbv.traverse(lambda node: cause_list.append(node))
        effect_list = []
        for vob in vob_list:
            vob.traverse(lambda node: effect_list.append(node))
        cause_list.sort(lambda node1, node2: node1.position - node2.position)
        effect_list.sort(lambda node1, node2: node1.position - node2.position)
        cause = "".join(map(lambda node: node.text, cause_list))
        effect = "".join(map(lambda node: node.text, effect_list))

        if cause in remove_word_dict or effect in remove_word_dict:
            cause = None
            effect = None
        else:
            is_done = True
            connective = connective_node.text

    return is_done, cause, effect, connective


# A造成的B句式
def rule_2(connective_node, remove_word_dict):
    is_done = False
    cause = None
    effect = None
    connective = None

    if connective_node.relation == "ATT":
        sbv_list = []
        for child in connective_node.children:
            if child.relation == "SBV":
                sbv_list.append(child)

        if len(sbv_list) > 0:
            cause_list = []
            for sbv in sbv_list:
                sbv.traverse(lambda node: cause_list.append(node))

            parent = connective_node.parent
            effect_list = [parent]
            for child in parent.children:
                if child != connective_node:
                    child.traverse(lambda node: node.position > connective_node.position and effect_list.append(node))

            cause_list.sort(lambda node1, node2: node1.position - node2.position)
            effect_list.sort(lambda node1, node2: node1.position - node2.position)
            cause = "".join(map(lambda node: node.text, cause_list))
            effect = "".join(map(lambda node: node.text, effect_list))

            if cause in remove_word_dict or effect in remove_word_dict:
                cause = None
                effect = None
            else:
                is_done = True
                connective = connective_node.text

    return is_done, cause, effect, connective


# 造成A的B句式
def rule_3(connective_node, remove_word_dict):
    is_done = False
    cause = None
    effect = None
    connective = None

    if connective_node.relation == "ATT":
        vob_list = []
        for child in connective_node.children:
            if child.relation == "VOB" or child.relation == "DBL":
                vob_list.append(child)

        if len(vob_list) > 0:
            parent = connective_node.parent
            cause_list = [parent]
            for child in parent.children:
                if child != connective_node:
                    child.traverse(lambda node: cause_list.append(node))

            effect_list = []
            for vob in vob_list:
                vob.traverse(lambda node: effect_list.append(node))

            cause_list.sort(lambda node1, node2: node1.position - node2.position)
            effect_list.sort(lambda node1, node2: node1.position - node2.position)
            cause = "".join(map(lambda node: node.text, cause_list))
            effect = "".join(map(lambda node: node.text, effect_list))

            if cause in remove_word_dict or effect in remove_word_dict:
                cause = None
                effect = None
            else:
                is_done = True
                connective = connective_node.text

    return is_done, cause, effect, connective


# usage:
segmentor = Segmentor()
postagger = Postagger()
parser = Parser()
# segmentor.load("path/to/model")
# postagger.load("path/to/model")
# parser.load("path/to/model")
# remove_word_dict = {}   # 用来过滤掉不希望出现在事件中的词
# dependency_tree_root = build_dependency_tree(sentence, segmentor, postagger, parser)
# connective_node = dependency_tree_root.find(lambda node: node.text in TRIGGER_WORDS)
# is_done, cause, effect, connective = rule_1(connective_node, remove_word_dict)
# if not is_done:
#     is_done, cause, effect, connective = rule_2(connective_node, remove_word_dict)
# ...
