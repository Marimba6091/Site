from urllib.parse import unquote, quote
import os
import datetime as dt
import signal
import json
import hashlib


class Net:
    def __init__(self, chest: str, href: str):
        self.chest = chest
        self.href = href
        self.__passwords = {"admin": ["admin"]}
        print(href)

    def date(self, str=True):
        dat = dt.datetime.now()
        return dat.isoformat(sep=" ") if str else dat
    
    def printl(*args, end="\n"):
        if args[1]:
            file = open("server/logs.txt", "a", encoding="utf-8")
            file.write(f"\n{args[1]}")
            file.close()
            print(args[1])
    
    def authenticator(self, adr):
        file = open("authenticator.json", "r")
        dct = json.load(file)
        file.close()
        if dct:
            for step in dct:
                for i in range(len(dct[step])):
                    dat = dt.datetime.now() - dt.datetime.fromisoformat(dct[step][i][1])
                    if dat.seconds // 60 > 5:
                        file = open("authenticator.json", "w")
                        dct[step].pop(i)
                        json.dump(dct, file)
                        file.close()
        for i in dct["admin"]:
            if adr[0] == i[0]:
                return "admin"
        return False

    def log_in_listing(self, name, password, ref):
        print(name, password, ref)
        if ref ==  self.href:
            file = open("authenticator.json", "r")
            dct = json.loads(file.read())
            file.close()
            if password in self.__passwords["admin"]:
                for i in dct["admin"]:
                    if i[0] == name[0]:
                        return
                dct["admin"] += [[name[0], self.date()]]
                file = open("authenticator.json", "w")
                json.dump(dct, file)
                file.close()
        return

    def sound(self, path):
        file = open(self.chest + path, "rb")
        sound = file.read()
        file.close()
        content = f"HTTP/1.1 200 OK\r\nContent-Type: sound/mp3\r\nContent-Length:{len(sound)}\r\nConnection: close\r\n\r\n"
        content = content.encode() + sound
        return content
    
    def cinema(self, path):
        file = open(self.chest + path, "rb")
        video = file.read()
        file.close()
        content = f"HTTP/1.1 200 OK\r\nContent-Type: video/mp4\r\nContent-Length:{len(video)}\r\nConnection: close\r\n\r\n"
        content = content.encode() + video
        return content
    
    def font(self, path):
        file = open(self.chest + path, "rb")
        font = file.read()
        file.close()
        exp = path.split(".")[1]
        content = f"HTTP/1.1 200 OK\r\nContent-Type: font/{exp}\r\nContent-Length:{len(font)}\r\nConnection: close\r\n\r\n"
        content = content.encode("utf-8") + font
        return content

    def image(self, path, http=True):
        file = open(self.chest + path, "rb")
        img = file.read()
        file.close()
        exp = path.split('.')[1]
        if http:
            content = f"HTTP/1.1 200 OK\r\nContent-Type: image/{exp}\r\nContent-Length:{len(img)}\r\nConnection: close\r\n\r\n"
            content = content.encode() + img
            return content
        return img

    def text(self, path, descriptions="", add_data=(), code_ask=200):
        self.printl(descriptions, end="")
        file = open(self.chest + path, "r", encoding="utf=8")
        string = file.read()
        file.close()
        if add_data:
            for i in add_data:
                string = string.replace(i[0], i[1])
        string = string.encode("utf-8")
        content = f"HTTP/1.1 {code_ask} OK\r\nContent-Type: text/html\r\nContent-Length:{len(string)}\r\n\r\n"
        return content.encode("utf-8") + string
    
    def media(self, path):
        file = open(f"{self.chest}/media.html", "r", encoding="utf-8")
        string = file.read()
        file.close()
        string = string.replace(".add_data.", self.href + path).replace(".title.", path.replace("/sounds/", "").split(".")[0].replace("%20", " "))
        string = string.encode("utf-8")
        content = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length:{len(string)}\r\n\r\n"
        return content.encode("utf-8") + string
    
    def listing(self, path):
        lst = {"dir":[], "file":[]}
        for i in os.listdir(path):
            if os.path.isfile(path + "/" + i):
                lst["file"] += [i]
                continue
            if os.path.isdir(path + "/" + i):
                lst["dir"] += [i]
                continue
        string = ""
        for i in lst:
            for k in lst[i]:
                add = ""
                if i == "dir":
                    string += f"<div class=\"features\">\n<a class=\"feature\" href=\"{self.href}{("listing/" + path[5:] + "/" + quote(k).replace("//", "/").replace("%28", "(").replace("%29", ")"))}\">\n<img class=\"icon\" src=\"{self.href}img/icons/folder.png\">\n<p>{k}</p>\n</a>\n</div>\n"
                else:
                    if k.split(".")[-1] == "mp3":
                        add = f"<a class=\"feature-play\" href=\"{self.href}media.html?&{quote(path[5:]) + "/" + k}\"><img class=\"icon\" src=\"{self.href}img/icons/play.png\"></a>\n"
                    string += f"<div class=\"features\">\n<a class=\"feature\" href=\"{self.href}{(path[5:] + "/" + quote(k).replace("%28", "(").replace("%29", ")"))}\">\n<img class=\"icon\" src=\"{self.href}img/icons/{self.get_icon(k.split(".")[-1])}.png\">\n<p><p>{k.replace("%20", " ")}</p>\r\n</a>{add}\n</div>\n"
        file = open(self.chest + "/listing.html", "r", encoding="utf-8")
        content = file.read()
        file.close()
        content = content.replace(".add_data.", string).replace(".title.", path)
        content = content.encode("utf-8")
        http_ask = f"HTTP/1.1 200 OK\nContent-Type: text/html\nContent-Length:{len(content)}\n\n"
        content = http_ask.encode("utf-8") + content
        return content

    def create_file(self, hash, inside_file, filename, num):
        inside_file = inside_file.decode()
        Ref = ""
        for i in inside_file.split("\r\n"):
            if "Referer: " in i:
                Ref = i
        Ref = Ref.replace("Referer: ", "")
        Ref = Ref.replace(self.href, "")
        Ref = "data" + Ref[7:]
        
        file = open("data/upload/uploadId.json", "r", encoding="utf-8")
        dct = json.loads(file.read())
        file.close()

        dct[hash] = {"name":filename, "number_of_chunks":num}

        file = open("data/upload/uploadid.json", "w", encoding="utf-8")
        json.dump(dct, file)
        file.close()

        with open(Ref + "/" + filename, "w") as file:
            file.write("")
    
    def adding_to_file(self, request, hash):
        content = b"\n".join(request.split(b"\r\n\r\n")[2].split(b"\r\n")[:-2])
        file = open("data/upload/uploadId.json", "r", encoding="utf-8")
        filename = json.load(file)[hash]["name"]
        file.close()

        ref = ""
        for i in request.split(b"\r\n"):
            if b"Referer: " in i:
                ref = i.decode()
                break
        ref = ref.replace("Referer: ", "")
        ref = ref.replace(self.href, "")
        if ref.split("/")[0] == "listing":
            ref = ref[7:]
        
        print("data" + ref + "/" + filename)
        with open("data/" + ref + "/" + filename, "ab") as file:
            file.write(content)

    def upload_finish(self, hash):
        file = open("data/upload/finish", "r", encoding="utf-8")
        dct = dict(json.loads(file.read()))
        file.close()

        dct = dct.pop(hash)

        file = open("data/upload/finish", "w", encoding="utf-8")
        json.dump(dct, file)
        file.close()

    def get_post_action(self, type):
        return {"password": self.log_in_listing}.get(type, False)
    
    @staticmethod
    def get_icon(exp):
        return {"jpeg": "image", "ico": "image", "jpg": "image", "html": "html", "mp3": "sound", "h": "html", "ttf": "font", "png": "image", "mp4":"video"}.get(exp, "unknown")
    
    @staticmethod
    def closed():
        files = open("server/logs.txt", "a", encoding="utf-8")
        files.write(f"\rServer was close at {dt.datetime.today()}\r")
        files.close()
    
    @staticmethod
    def activation():
        files = open("server/logs.txt", "a", encoding="utf-8")
        files.write(f"\nServer was open at {dt.datetime.today()}\n")
        files.close()

def show_content(request, name, host):
    net = Net("data", f"http://{host[0]}/")
    get_req = request
    lines = get_req.split(b"\r\n")
    method, path, http_v = lines[0].decode().split(" ")
    path = unquote(path)
    path = path.replace("//", "/")
    if method == "POST":
        if path == "/upload/start":
            dct_start_upload = request.split(b"\r\n\r\n")[-1].split(b"\"")
            filename = dct_start_upload[3].decode()
            number_of_chunks = int(dct_start_upload[8][1:-1])
            hash = hashlib.sha256(filename.encode("utf_8")).hexdigest()
            net.create_file(hash, request, filename, number_of_chunks)
            return net.text("/upload/start", add_data=((".upload_id.", hash),))
        elif path == "/upload/chunk":
            print(request)
            hash = request.split(b"\r\n\r\n")[-4].split(b"\r\n")[0].decode()
            net.adding_to_file(request, hash)
            return net.text("/upload/chunk", add_data=((".upload_id.", hash),))
        # elif path == "/upload/finish":
        #     dct = json.loads(request.split(b"\r\n\r\n")[-1].decode())
        #     Ref = ""
        #     for i in request.decode().split("\r\n"):
        #         if "Referer: " in i:
        #             Ref = i
        #     Ref = Ref.replace("Referer: ", "")
        #     Ref = Ref.replace(net.href, "")
        #     Ref = "data" + Ref[7:]
        #     net.upload_finish(dct["uploadId"])
        #     net.text("/upload/finish", add_data=((".upload_id.", dct["uploadId"]), (".name.", dct["filename"]), ("##", str(dct["fileSize"]))))
        elif len(lines) > 14:
            if b"=" in lines[14]:
                for i in lines:
                    if b"Host: " in i:
                        Dhost = "http://" + i.decode().replace("Host: ", "") + "/"
                        messege = lines[14].decode().split("=")
                        if messege[1]:
                            net.printl(f"type: \"{messege[0]}\"; messege: \"{messege[1]}\"; path: {path}{(31 - len(messege[0]) - len(messege[1]) - len(path)) * " "}| User adress - {name} | {net.date()} | <POST>")
                            func = net.get_post_action(messege[0])
                            if func:
                                func(name, messege[1], Dhost)
                        break
    rules = net.authenticator(name)
    Dpath = path.split("/")
    while "" in Dpath:
        Dpath.remove('')
    net.printl(f"{path}{(60 - len(path)) * ' '}| User adress - {name} | {net.date()} | <{method}>")
    if path == "/":
        return net.text("/index.html")
    elif "listing" == Dpath[0]:
        if rules == ("admin"):
            path = "data/" + "/".join(Dpath[1:])
            print(path)
            if os.path.isdir(path):
                return net.listing(path)
        else:
            return net.text("/authenticator.html")
    elif os.path.isfile(net.chest + path):
        if "." in path:
            if "/private/" in path:
                if rules != ("admin"):
                    return net.text("/authenticator.html")
            exp = Dpath[-1].split(".")[-1]
            extension = get_extensions(net, exp)
            if extension:
                return extension(path)
        return net.text(path)
    elif Dpath[0].split("?&")[0] == ("media.html"):
        path = path.replace("media.html?&", "")
        if os.path.isfile(net.chest + path):
            return net.media(path)
    return net.text("/Error.html", descriptions="Error", add_data=((".actual_domen.", net.href),), code_ask=404)
    

def get_extensions(obj: Net, extension):
    func = {"jpeg": obj.image, "ico": obj.image, "jpg": obj.image, "html": obj.text, "mp3": obj.sound, "h": obj.text, "ttf": obj.font, "png": obj.image, "mp4": obj.cinema}.get(extension, False)
    return func

if __name__ == "__main__":
    print("Start from file \"main.py\", please")