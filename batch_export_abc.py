import hou
import os


def cleanUp():
    geoNode.destroy()
    exit()


sFrame = hou.expandString("$RFSTART")
eFrame = hou.expandString("$RFEND")
obj = hou.node("/obj")
geoNode = obj.createNode("geo", "helper")
objMerge = geoNode.createNode("object_merge", "import_geo")
ropAbc = geoNode.createNode("rop_alembic", "out_rop")
ropAbc.setInput(0, objMerge)
geoNode.hide(True)

selectedNodes = hou.ui.selectNode(
    multiple_select=True,
    node_type_filter=hou.nodeTypeFilter.Sop,
)
if selectedNodes == None:
    hou.ui.displayConfirmation("No Nodes Selected",
                               severity=hou.severityType.Error,
                               title="Error")
    cleanUp()

selectedNodesStr = "\n".join(selectedNodes)
confirm = hou.ui.displayConfirmation(f"Selected Nodes:\n{selectedNodesStr}")
if confirm == False:
    cleanUp()

for node in selectedNodes:
    nodeName = os.path.basename(node)
    objMerge.parm("objpath1").set(node)
    ropAbc.parm("filename").set(f"$HIP/abc/{nodeName}.abc")
    ropAbc.render(frame_range=(int(sFrame), int(eFrame)))

cleanUp()
