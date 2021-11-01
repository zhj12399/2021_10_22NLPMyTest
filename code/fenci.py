import csv
import time

start_time = time.time()


# 读入字典
def load_dictionary():
    word_list = set()
    csvFile = open("test.csv", "r")
    reader = csv.reader(csvFile)
    for item in reader:
        word_list.add(item[0])
    return word_list


# 完全切分式中文分词
# 如果在词典中则认为是一个词
def fully_segment(text, dic):
    word_list = []
    for i in range(len(text)):
        for j in range(i + 1, len(text) + 1):
            word = text[i:j]
            if word in dic:
                word_list.append(word)
    return word_list


# 正向最长匹配
# 从当前扫描位置的单字所有可能的结尾，我们找最长的
def forward_segment(text, dic):
    word_list = []
    i = 0
    while i < len(text):
        longest_word = text[i]
        for j in range(i + 1, len(text) + 1):
            word = text[i:j]
            if word in dic:
                if len(word) > len(longest_word):
                    longest_word = word
        word_list.append(longest_word)
        i += len(longest_word)
    return word_list


# 逆向最长匹配
def back_segment(text, dic):
    word_list = []
    i = len(text) - 1
    while i >= 0:
        longest_word = text[i]
        for j in range(0, i):
            word = text[j:i + 1]
            if word in dic:
                if len(word) > len(longest_word):
                    longest_word = word
        word_list.append(longest_word)
        i -= len(longest_word)
    word_list.reverse()
    return word_list


# 统计单字成词的个数
def count_single_char(word_list: list):
    return sum(1 for word in word_list if len(word) == 1)


# 双向最长匹配，实际上是做了个融合
def bidirectional_segment(text, dic):
    f = forward_segment(text, dic)
    b = back_segment(text, dic)
    # 词数更少更优先
    if len(f) < len(b):
        return f
    elif len(f) > len(b):
        return b
    else:
        # 单字更少更优先
        if count_single_char(f) < count_single_char(b):
            return f
        else:  # 都相等时我们更倾向于逆向匹配的
            return b


dic = load_dictionary()
print(len(dic))
print("完全切分：", fully_segment("就读于北京大学", dic))
print("前向切分：", forward_segment("就读于北京大学", dic))
print("前向切分：", forward_segment("研究生物起源", dic))
print("后向切分：", back_segment("研究生物起源", dic))
print("双向切分：", bidirectional_segment("研究生物起源", dic))

test_file = open("renmin.csv", "r")
reader = csv.reader(test_file)
test_sents = []
ans_sents = []
for item in reader:
    test_sent = ""
    ans_sent = []
    for word in item:
        test_sent += word.strip()
        ans_sent.append(word)
    test_sents.append(test_sent)
    ans_sents.append(ans_sent)


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
for i in range(test_sents_num):
    xun_lian = bidirectional_segment(test_sents[i], dic)
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
    P += p
    R += r
    if i % 100 == 0:
        print(i / test_sents_num)

# 求一个平均值
P = P / test_sents_num
R = R / test_sents_num
F_1 = 2 * P * R / (P + R)
print("P,R,F1", P, R, F_1)
end_time = time.time()
print(end_time - start_time)
