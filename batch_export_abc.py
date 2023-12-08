import hou , os

sFrame = hou.expandString("$RFSTART")
eFrame = hou.expandString("$RFEND")

obj = hou.node("/obj")
geoNode = obj.createNode('geo','helper')
objMerge = geoNode.createNode('object_merge','import_geo')
ropAbc = geoNode.createNode('rop_alembic','out_rop')
ropAbc.setInput(0,objMerge)
geoNode.hide(True)

selectedNodes = hou.ui.selectNode(multiple_select=True,node_type_filter=hou.nodeTypeFilter.Sop)
confirm = hou.ui.displayConfirmation(f"Selected Nodes:  {selectedNodes}")
if confirm == False:
    geoNode.destroy()
    exit()


for node in selectedNodes:
    nodeName = os.path.basename(node)
    objMerge.parm('objpath1').set(node)
    ropAbc.parm('filename').set(f'$HIP/abc/{nodeName}.abc')
    ropAbc.render(frame_range=(int(sFrame),int(eFrame)))

geoNode.destroy()



"""

"""