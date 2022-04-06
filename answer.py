import sqlite3

guess = "zones"
answer = "zebra"

for x in range(len(answer)):
    if f"{answer}"[x] == f"{guess}"[x]:
        print(f"{guess}"[x], " - correct position")
    elif f"{guess}"[x] in f"{answer}":
        print(f"{guess}"[x], " - exists")
    else:
        print(f"{guess}"[x], " - not found")
