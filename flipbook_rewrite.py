class Flipbook:
    def frameRange(self, frameRange):
        frList = str(frameRange).split("-")
        self.start = frList[0]
        self.end = frList[1]
        return self

    def height(self, res_height):
        self.resolutionHeight = res_height
        return self

    def width(self, res_width):
        self.resolutionWidth = res_width
        return self

    def frameRate(self, frameRate):
        self.frameRate = frameRate
        return self

    def frameIncrement(self, frameIncrement):
        self.frameIncrement = frameIncrement
        return self

    def testFunction(self):
        print("test")


class Handler:
    def __init__(self):
        self.tempDir = ""
        self.workDir = ""
        self.outDir = ""
        self.backups = ""

    @staticmethod
    def checkDependency():


obj = Flipbook().height(180).width(180).frameRange("100-600")
print(obj.end)
