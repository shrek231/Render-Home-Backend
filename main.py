import flask
import os
from flask import request, jsonify, send_from_directory
app = flask.Flask(__name__)
app.config["DEBUG"] = False

framestorender=[]
unrenderedframes=0
totalframes=1

ROOT_DIRECTORY = "/home/runner/BlenderRenderServer/"

@app.route('/', methods=['GET']) # root page
def root():
  global unrenderedframes
  global totalframes
  return f"<h1>Blender Render Server</h1>" +  str(int((unrenderedframes-totalframes)/totalframes * -100)) + "% complete"

@app.route("/getBlend", methods=['GET']) # serve blend file
def get_blend_file():
  return send_from_directory(ROOT_DIRECTORY,"render.blend")


@app.route("/cancel", methods=['GET']) # serve blend file
def cancel_renders():
  global framestorender
  global unrenderedframes
  global totalframes
  totalframes = 1
  framestorender = []
  unrenderedframes = 0
  return "OK"

@app.route("/Render.zip", methods=['GET']) # serve blend file
def get_rendered_files():
  os.system("rm images.zip")
  os.system("zip -r images.zip Images/")
  return send_from_directory(ROOT_DIRECTORY,"images.zip")

@app.route('/sendBlend', methods=['POST']) # get blend file from master
def recieve_blend_file():
  global framestorender
  global unrenderedframes
  global totalframes
  for file in request.files:
    framerange = file.split("-")
    framestorender=list(range(int(framerange[0]),int(framerange[1])+1))
    unrenderedframes=len(framestorender)
    totalframes = len(framestorender)
    request.files[file].save(ROOT_DIRECTORY+"render.blend")
  os.system("rm Images/*")
  return "OK"

@app.route('/sendFrame', methods=['POST']) # get frame from client
def recieve_frame():
  global unrenderedframes
  for image in request.files:
    request.files[image].save(ROOT_DIRECTORY+"Images/"+f"{int(image):04}"+".png")
    unrenderedframes = unrenderedframes - 1
  return "OK"

@app.route('/requestFrame', methods=['GET']) # sind a frame to a client
def distrubite_frame():
  if len(framestorender) > 0:
    responce = framestorender[0]
    del framestorender[0]
    return jsonify(responce)
  else:
    return jsonify(-1)

@app.route('/status', methods=['GET']) # sind a frame to a client
def render_status():
  return jsonify(unrenderedframes)

@app.route('/cancelFrame', methods=['POST']) # add a frame back into the frames to render
def cancel_render():
  global framestorender
  if int(request.json["frame"]) not in framestorender:
    framestorender.append(int(request.json["frame"]))
  return "OK"
  #else:
  #  return "Already going to render this frame"


app.run(host='0.0.0.0', port=8080)
