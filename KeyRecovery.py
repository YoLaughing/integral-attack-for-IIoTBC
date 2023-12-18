p3 = [[0, 8, 16, 24, 1, 9, 17, 25],
      [2, 10, 18, 26, 3, 11, 19, 27],
      [4, 12, 20, 28, 5, 13, 21, 29],
      [6, 14, 22, 30, 7, 15, 23, 31]]

k15 = [28, 29, 30, 31]
Kr = [[28, 29, 30, 31],
      [16, 17, 18, 19, 20, 21, 22, 23],
      [8, 9, 10, 11, 12, 13, 14, 15, 24, 25, 26, 27, 28, 29, 30, 31],
      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
      ]

y = [[0, 1, 2, 3], [8, 9, 10, 11], [16, 17, 18, 19], [24, 25, 26, 27],
     [0, 1, 2, 3], [8, 9, 10, 11], [16, 17, 18, 19], [24, 25, 26, 27],
     [0, 1, 2, 3], [8, 9, 10, 11], [16, 17, 18, 19], [24, 25, 26, 27],
     [0, 1, 2, 3], [8, 9, 10, 11], [16, 17, 18, 19], [24, 25, 26, 27],
     [4, 5, 6, 7], [12, 13, 14, 15], [20, 21, 22, 23], [28, 29, 30, 31],
     [4, 5, 6, 7], [12, 13, 14, 15], [20, 21, 22, 23], [28, 29, 30, 31],
     [4, 5, 6, 7], [12, 13, 14, 15], [20, 21, 22, 23], [28, 29, 30, 31],
     [4, 5, 6, 7], [12, 13, 14, 15], [20, 21, 22, 23], [28, 29, 30, 31]]

# id = 4
print("K_4: ")
reg_4 = Kr[0]
reg_1 = Kr[3]
# temp = []
guessNum = 52
notGuessNum = 0
NewKr = []
NotKr = []
temp_p = []
new_guess = []
not_guess = []
reg = [i for i in range(16)] + [i for i in range(24,32)]
for p in reg:
    need = y[p]
    tt = [b for b in need if b not in reg_4]
    if len(tt) ==0 and p in reg_1:
        temp_p.append(p)
        not_guess.append(p)
        notGuessNum += 1
    else:
        temp_p.append(p)
        new_guess.append(p)
        guessNum += 1
Kr.append(temp_p)
# print(Kr)
print("notGuess 4: ")
print(not_guess)
print("newGuess 4: ")
print(new_guess)
NewKr.append(new_guess)
NotKr.append(not_guess)

for r in range(5,8):
    print("round {0} ----------------".format(r))
    reg_4 = Kr[r-4]
    reg_1 = Kr[r-1]
    temp_p = []
    new_guess = []
    not_guess = []
    for p in range(32):
        need = y[p]
        tt = [b for b in need if b not in reg_4]
        if len(tt) == 0 and p in reg_1:
            temp_p.append(p)
            not_guess.append(p)
            notGuessNum += 1
        else:
            temp_p.append(p)
            new_guess.append(p)
            guessNum += 1
    Kr.append(temp_p)
    # print(Kr)
    print("notGuess {0}".format(r))
    print(not_guess)
    print("newGuess {0}: ".format(r))
    print(new_guess)
    print("All guessNum = {0}, newGuess = {1}".format(guessNum, len(new_guess)))
    NewKr.append(new_guess)
    NotKr.append(not_guess)

print(Kr)
print(NewKr)
print(NotKr)

r = 15
print("--------------------")
for i in range(4):
    # temp = Kr[i]
    temp = str(r)
    temp += " & "
    temp += ", ".join([str(p) for p in Kr[i]])
    temp += " & \\\\ \\hline"

    print(temp)
    r += 1
    # print(", ".join(Kr[i]))
    # print(", ".join(Kr[i]) + " & & \\\\")

for i in range(4):
    temp = str(r)
    temp += " & "
    temp += ", ".join([str(p) for p in NewKr[i]])
    temp += " & "
    temp += ", ".join([str(p) for p in NotKr[i]])
    temp += " \\\\ \\hline"
    # print("&")
    # print(NewKr[i])
    # print("&")
    # print(NotKr[i])
    # print("\\\\")
    print(temp)
    r += 1

# notGuessNum += 0
print("notGuessNum = {0}".format(notGuessNum))