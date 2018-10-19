import subprocess as sp

p = sp.Popen("./backend", stdin=sp.PIPE, stdout=sp.PIPE)

while True:
    try:
        s = input("Enter two numbers: ")
        if s == "quit" or s == "exit":
            break
        a, b = s.split()
        a, b = int(a), int(b)
        data = "{} {}\n".format(a, b).encode("ascii")
        p.stdin.write(data)
        p.stdin.flush()
        t = p.stdout.readline().decode("ascii").strip()
        print("The result is {}".format(t))
    except (IndexError, ValueError):
        print("Invalid input!")
    except KeyboardInterrupt:
        break
