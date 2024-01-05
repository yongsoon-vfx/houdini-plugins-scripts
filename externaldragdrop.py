import hou, os, re

# Dictionary for Matching File to Node
# Syntax is extension: [nodeType,nodeParm]
typeMatchSOP = {
    "obj": ["file", "file"],
    "abc": ["file", "file"],
    "fbx": ["file", "file"],
    "png": ["uvquickshade", "texture"],
    "jpg": ["uvquickshade", "texture"],
    "bmp": ["uvquickshade", "texture"],
    "exr": ["uvquickshade", "texture"],
    "tiff": ["uvquickshade", "texture"]
}

typeMatchSHOP = {
    "png": ["redshift::TextureSampler", "tex0"],
    "jpg": ["redshift::TextureSampler", "tex0"],
    "bmp": ["redshift::TextureSampler", "tex0"],
    "exr": ["redshift::TextureSampler", "tex0"],
    "tiff": ["Redshift::TextureSampler", "tex0"]
}

# Will look for files with the following sub-strings
# and set the colorspace to Raw
linearTextures = {
    "roughness",
    "glossiness",
    "normal",
    "nrm",
    "bump",
    "gloss",
    "refl",
    "metalness",
    "disp",
    "displacement",
}

#Declare Node Context Categories
geoContext = ("geo", "placeholder")
shaderContext = ("mat", "redshift_vopnet", "subnet")
validContext = geoContext + shaderContext


def dropAccept(files):
    pane = hou.ui.paneTabUnderCursor()
    network = pane.pwd()
    context = network.type().name()
    cursor_position = pane.cursorPosition()

    if context not in validContext:
        return None

    for file in files:
        creategeoNode(file, network, context, cursor_position)

    return True


def creategeoNode(file, network, context, pos):
    nodeName = os.path.basename(file)
    ext = nodeName.split('.')[-1]
    nodeName = re.sub(r"[^0-9a-zA-Z\.]+", "_", nodeName)
    if context in geoContext:
        nodeAttrs = typeMatchSOP.get(ext)
    elif context in shaderContext:
        nodeAttrs = typeMatchSHOP.get(ext)
    if nodeAttrs == None:
        hou.ui.displayConfirmation(f"Invalid place to import {nodeName}",
                                   severity=hou.severityType.Error)
        return False

    nodeType = nodeAttrs[0]
    nodeParm = nodeAttrs[1]
    #print(f"{nodeName}, {nodeType}, {nodeParm}")
    hou_node = network.createNode(nodeType, nodeName)
    path_parm = hou_node.parm(nodeParm)
    path_parm.set(file)

    if context in shaderContext:
        for item in linearTextures:
            if item in nodeName.casefold():
                color_parm = hou_node.parm("tex0_colorSpace")
                color_parm.set("raw")
                break

    hou_node.setPosition(pos)
    #print(f"Imported: {nodeName}")
    return None
