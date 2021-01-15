import os
import bpy
import time
import requests

server_url = "http://blenderrenderserver.youtubeadminist.repl.co"

WaitForRender = False

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

scene = bpy.context.scene
blendpath = (bpy.data.filepath)
framerange = str(scene.frame_start) + "-" + str(scene.frame_end)



if requests.get(f"{server_url}/status").json() == 0:
    os.system(f"curl -F {framerange}=@{blendpath} {server_url}/sendBlend")
    print() # add newline after curl prints "OK"


    if WaitForRender:
        while True:
            frame = requests.get(f"{server_url}/status").json()
            print(str(int((frame/(scene.frame_end-scene.frame_start+1)-1)*-100)) + "% complete")
            if frame == 0:
                break
            time.sleep(5)
        print(f"done\nget your files at\n{server_url}/Render.zip")
else:
    if requests.get(f"{server_url}/status").json() < 1:
        os.system(f"curl {server_url}/cancel")
        print("something weird happened, canceling render")
    else:
        print(f"already rendering\ncancel the render by going to {server_url}/cancel")
