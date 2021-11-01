import csv
import time

start_time = time.time()
fenci_file = open("renmin.csv", "r")
fenci_reader = csv.reader(fenci_file)
fenci_sents = []
for item in fenci_reader:
    sent = []
    for i in item:
        sent.append(i.strip())
    fenci_sents.append(sent)

sum_zero = 0
for sent in fenci_sents:
    if len(sent) == 0:
        sum_zero += 1
    print(sent)
print(sum_zero)


# 一元语法模型
def sgram(sents: list):
    dic = {}
    dic['#始始#'] = 0
    dic['#末末#'] = 0
    for sent in sents:
        for item in sent:
            if item in dic:
                dic[item] = dic[item] + 1
            else:
                dic[item] = 1
        dic['#始始#'] += 1
        dic['#末末#'] += 1
    return dic


si_gram = sgram(fenci_sents)


# print(si_gram)


# 二元语法模型
def bgram(sents: list):
    dic = {}
    dic["#始始#"] = dict()
    for sent in sents:
        for i in range(0, len(sent) - 1):
            if sent[i] not in dic:
                dic[sent[i]] = dict()
                dic[sent[i]][sent[i + 1]] = 1
            else:
                if sent[i + 1] in dic[sent[i]]:
                    dic[sent[i]][sent[i + 1]] += 1
                else:
                    dic[sent[i]][sent[i + 1]] = 1

        if sent[0] not in dic["#始始#"]:
            dic["#始始#"][sent[0]] = 1
        else:
            dic["#始始#"][sent[0]] += 1

        if sent[len(sent) - 1] not in dic:
            dic[sent[len(sent) - 1]] = dict()
            dic[sent[len(sent) - 1]]["#末末#"] = 1
        elif "#末末#" not in dic[sent[len(sent) - 1]]:
            dic[sent[len(sent) - 1]]["#末末#"] = 1
        else:
            dic[sent[len(sent) - 1]]["#末末#"] += 1
    return dic


bi_gram = bgram(fenci_sents)


# print(bi_gram)


# 查看一元词频
def select_si_gram(gram: dict, word):
    return gram[word]


def selecr_bi_gram(gram: dict, word_one, word_two):
    return gram[word_one][word_two]


cixing_file = open("renmincixing.csv", "r")
cixing_reader = csv.reader(cixing_file)
cixing_sents = []
for item in cixing_reader:
    sent = []
    for i in item:
        sent.append(i.strip())
    cixing_sents.append(sent)

# print(sents)

part = dict()
# 统计所有词性个数
for sent in cixing_sents:
    for word in sent:
        word_part = word.split('/')[-1].split(']')[0].split('!')[0]
        if word_part in part:
            part[word_part] += 1
        else:
            part[word_part] = 1

part_len = len(part)
print(part, "一共多少类：", part_len)
print("总频次", sum(part.values()))

# 或得转移矩阵
trans = dict()
for sent in cixing_sents:
    for i in range(len(sent) - 1):
        one = sent[i].split('/')[-1].split(']')[0].split('!')[0]
        two = sent[i + 1].split('/')[-1].split(']')[0].split('!')[0]
        if one in trans:
            if two in trans[one]:
                trans[one][two] += 1
            else:
                trans[one][two] = 1
        else:
            trans[one] = dict()
            trans[one][two] = 1
print(trans)

# 每个词的词性概率
percent = dict()
for sent in cixing_sents:
    for word in sent:
        word_word = word.split('/')[0].split('{')[0].strip('[')
        word_part = word.split('/')[-1].split(']')[0].split('!')[0]
        if word_word in percent:
            if word_part in percent[word_word]:
                percent[word_word][word_part] += 1
            else:
                percent[word_word][word_part] = 1
        else:
            percent[word_word] = dict()
            percent[word_word][word_part] = 1


# print(percent)

def fen_ci(text):
    # 生成一元语法词网
    def generate_wordnet(gram, text):
        net = [[] for _ in range(len(text) + 2)]
        for i in range(len(text)):
            for j in range(i + 1, len(text) + 1):
                word = text[i:j]
                if word in gram:
                    net[i + 1].append(word)
        i = 1
        while i < len(net) - 1:
            if len(net[i]) == 0:  # 空白行
                j = i + 1

                for j in range(i + 1, len(net) - 1):
                    # 寻找第一个非空行j
                    if len(net[j]):
                        break
                # 填补i，j之间的空白行
                net[i].append(text[i - 1:j - 1])
                i = j
            else:
                i += len(net[i][-1])
        return net

    # 测试一个句子
    si_net = generate_wordnet(si_gram, text)

    # print(si_net)

    def calculate_gram_sum(gram: dict):
        num = 0
        for g in gram.keys():
            num += sum(gram[g].values())
        return num

    # 计算word_one后出现word_two的概率，带上+1平滑处理
    def calculate_weight(gram: dict, word_one, word_two, gram_sum):
        if word_one in gram:
            word_one_all = gram[word_one].values()
            if word_two in gram[word_one]:
                return (gram[word_one][word_two] + 1) / (sum(word_one_all) + gram_sum)
            else:
                return 1 / (sum(word_one_all) + gram_sum)
        else:
            return 1 / gram_sum

    bi_gram_sum = calculate_gram_sum(bi_gram)

    # print(bi_gram_sum)

    def viterbi(wordnet):
        dis = [dict() for _ in range(len(wordnet))]
        node = [dict() for _ in range(len(wordnet))]
        word_line = [dict() for _ in range(len(wordnet))]
        wordnet[len(wordnet) - 1].append("#末末#")
        # 更新第一行
        for word in wordnet[1]:
            dis[1][word] = calculate_weight(bi_gram, "#始始#", word, bi_gram_sum)
            node[1][word] = 0
            word_line[1][word] = "#始始#"
        # 遍历每一行wordnet
        for i in range(1, len(wordnet) - 1):
            # 遍历每一行中单词
            for word in wordnet[i]:
                # 更新加上这个单词的距离之后那个位置的所有单词的距离
                for to in wordnet[i + len(word)]:
                    if word in dis[i]:
                        if to in dis[i + len(word)]:
                            # 要的是最大的概率
                            if dis[i + len(word)][to] < dis[i][word] * calculate_weight(bi_gram, word, to, bi_gram_sum):
                                dis[i + len(word)][to] = dis[i][word] * calculate_weight(bi_gram, word, to, bi_gram_sum)
                                node[i + len(word)][to] = i
                                word_line[i + len(word)][to] = word
                        else:
                            dis[i + len(word)][to] = dis[i][word] * calculate_weight(bi_gram, word, to, bi_gram_sum)
                            node[i + len(word)][to] = i
                            word_line[i + len(word)][to] = word

        # 回溯
        path = []
        f = node[len(node) - 1]["#末末#"]
        fword = word_line[len(word_line) - 1]["#末末#"]
        path.append(fword)
        while f:
            tmpword = fword
            fword = word_line[f][tmpword]
            f = node[f][tmpword]
            path.append(fword)
        path = path[:-1]
        path.reverse()
        return dis, node, word_line, path

    (dis, _, _, path) = viterbi(si_net)
    # print(dis)
    # print(path)
    return path


def ci_xing(text):
    text_percent = []

    # 这里我们假设是所有单词都已经人民日报语料库了
    for word in text:
        word_percent = percent[word]
        text_percent.append(word_percent)

    # print(text_percent)

    # 下面我们来使用Viterbi算法计算出最佳的组成
    dis = [dict() for _ in range(len(text))]
    node = [dict() for _ in range(len(text))]
    for first in text_percent[0].keys():
        dis[0][first] = 1
    for i in range(len(text) - 1):
        word_one = text[i]
        word_two = text[i + 1]
        word_one_percent_dict = text_percent[i]
        word_two_percent_dict = text_percent[i + 1]

        word_one_percent_key = list(word_one_percent_dict.keys())
        word_one_percent_value = list(word_one_percent_dict.values())
        word_two_percent_key = list(word_two_percent_dict.keys())
        word_two_percent_value = list(word_two_percent_dict.values())
        for word_two_per in word_two_percent_key:
            tmp_dis = []
            for word_one_per in word_one_percent_key:
                if word_two_per in trans[word_one_per]:
                    tmp_num = dis[i][word_one_per] * (
                            (trans[word_one_per][word_two_per] + 1) / (part[word_one_per] + part_len)) * (
                                      text_percent[i + 1][word_two_per] / part[word_two_per])
                    tmp_dis.append(tmp_num)
                else:
                    tmp_num = dis[i][word_one_per] * (1 / (part[word_one_per] + part_len)) * (
                            text_percent[i + 1][word_two_per] / part[word_two_per])
                    tmp_dis.append(tmp_num)

            max_tmp_dis = max(tmp_dis)
            max_tmp_dis_loc = tmp_dis.index(max_tmp_dis)
            dis[i + 1][word_two_per] = max_tmp_dis
            node[i + 1][word_two_per] = word_one_percent_key[max_tmp_dis_loc]
    # print(dis, node)

    # 根据node来倒找答案
    path = []
    f_value = list(dis[len(dis) - 1].values())
    f_key = list(dis[len(dis) - 1].keys())
    f = f_key[f_value.index(max(f_value))]

    path.append(f)
    for i in range(len(dis) - 1, 0, -1):
        f = node[i][f]
        path.append(f)
    path.reverse()
    return path


# 对所有训练集进行测试
test_file = open("renmincixing.csv", "r")
reader = csv.reader(test_file)
test_sents = []
ans_sents = []
fenci_sents = []
for item in reader:
    test_sent = ""
    ans_sent = []
    fenci_sent = []
    for word in item:
        word_word = word.split('/')[0].split('{')[0].strip('[')
        word_part = word.split('/')[-1].split(']')[0].split('!')[0]
        if word_word == '。' and word_word == '！' and word_word == '？':
            test_sent += word_word.strip()
            ans_sent.append(word_word)
            fenci_sent.append(word_part)
            break
        else:
            test_sent += word_word.strip()
            ans_sent.append(word_word)
            fenci_sent.append(word_part)
    test_sents.append(test_sent)
    ans_sents.append(ans_sent)
    fenci_sents.append(fenci_sent)


# 将分词出来的结果转换为集合中元素
def zhuan_huan(text: list):
    ans = []
    i = 1
    for word in text:
        ans.append([i, i + len(word) - 1])
        i += len(word)
    return ans


test_sents_num = len(test_sents)
print(test_sents_num)
P = 0
R = 0
A = 0
A_num = 0
for i in range(test_sents_num):
    xun_lian = fen_ci(test_sents[i])
    xun_lian_list = zhuan_huan(xun_lian)
    ans_list = zhuan_huan(ans_sents[i])

    xun_lian_set = set()
    for tmp in xun_lian_list:
        xun_lian_set.add(tuple(tmp))

    ans_list_set = set()
    for tmp in ans_list:
        ans_list_set.add(tuple(tmp))

    TP = ans_list_set & xun_lian_set
    p = len(TP) / len(xun_lian_list)
    r = len(TP) / len(ans_list)
    # 我们只对分词正确的结果进行词性正确性评估
    if ans_list_set == xun_lian_set:
        A_num += 1
        # 预测来的
        ci_xing_list = ci_xing(ans_sents[i])
        # 正确答案
        ci_xing_ans = fenci_sents[i]
        a = 0
        for j in range(len(ci_xing_list)):
            if ci_xing_list[j] == ci_xing_ans[j]:
                a += 1

        a = a / len(ci_xing_list)
        A += a
    P += p
    R += r
    if i % 100 == 0:
        print(i / test_sents_num)

# 求一个平均值
P = P / test_sents_num
R = R / test_sents_num
F_1 = 2 * P * R / (P + R)
print("P,R,F1", P, R, F_1)
A = A / A_num
print("A", A)
end_time = time.time()
print(end_time - start_time)
