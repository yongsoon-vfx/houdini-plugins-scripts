import bpy , socket

filePath = bpy.data.filepath
abcPath = filePath.replace("blend","abc")
bpy.ops.wm.alembic_export(filepath=abcPath)


HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

bpy.ops.wm.quit_blender()

