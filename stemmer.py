import json

class Stemmer:
    def __init__(self, filename):
        self.filename = filename
        self.load()
    
    def load(self):
        self.file = open(filename, "r")
        self.data = json.loads(self.file.read())
        self.file.close()

    def find(self, word):
        out = None
        try:
            out = self.data[word]
        except:
            pass
        return out

if __name__ == "__main__":
    filename = "root_dict.json"
    s = Stemmer(filename)
    print(s.find("fajnie"))



