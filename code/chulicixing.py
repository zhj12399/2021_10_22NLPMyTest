import csv

mat = []

with open("renmincixing.txt", "r") as f:  # 打开文件
    for line in f:
        line = line[22:]
        print(line)
        mat.append([l for l in line.split()])

print(mat)

with open('renmincixing.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for row in mat:
        if len(row) != 0:
            writer.writerow(row)
