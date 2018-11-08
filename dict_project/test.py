

f = open('./dict.txt', 'rb')
while True:
    data = f.readline()
    if not data:
        break
    print(data.encode('utf8'))
    try:
        data.encode('utf8')
    except Exception:
        # print(str(data))
        pass