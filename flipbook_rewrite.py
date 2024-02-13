import subprocess, logging, os, concurrent.futures
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


class SceneObj:

    def __init__(self):
        print("Initialised Flipbook")

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
        self.coreCount = os.cpu_count()

        self.HIPDIR = ""
        self.HIPNAME = ""
        self.HIPFILE = ""

        self.tempDir = ""
        self.workDir = ""
        self.outDir = ""
        self.backups = ""

    @staticmethod
    def checkDependency():
        checkDep = subprocess.run("ffmpeg -h", stdout=None)
        if checkDep.returncode != 0:
            return None
        else:
            return True


class ImgProcessor:
    def __init__(self, images, coreCount):
        self.images = images
        self.coreCount = coreCount

    def execute(self):
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.input_threads.value()
        ) as executor:
            executor.map(self.processImg, self.images)

    def processImg(cimage):
        with Image.open(cimage).convert("RGBA") as base:
            cFrame = str(Path(cimage).name).lstrip("flipbook_").rstrip(".jpg")
            txt = Image.new("RGBA", base.size, (255, 255, 255, 0))
            d = ImageDraw.Draw(txt)
            height = base.size[1]
            fntWatermark = ImageFont.truetype("C:\WINDOWS\FONTS\Verdana.TTF", 40)
            d.text(
                (10, height - 50),
                "Heckler SG",
                fill=(255, 255, 255, 128),
                font=fntWatermark,
            )
            # txt.show()
            out = Image.alpha_composite(base, txt)
            out = out.convert("RGB")
            out.save(cimage)
            logging.info(f"Frame {cFrame} Processed")


obj = SceneObj().height(180).width(180).frameRange("100-600")
print(Handler.checkDependency())
