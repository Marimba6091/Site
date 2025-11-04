lst = ["ABCD"]
d = ""
while True:
    d = lst[-1]
    d = d[-1:] + d[:-1]
    if d == lst[0]:
        break
    lst.append(d)
print(lst)