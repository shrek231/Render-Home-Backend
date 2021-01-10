import flask
import os
from flask import Flask, request, abort, jsonify, send_from_directory
app = flask.Flask(__name__)
app.config["DEBUG"] = True

framestorender=[-1]

ROOT_DIRECTORY = "/home/runner/BlenderRenderServer/"

@app.route('/', methods=['GET']) # root page
def root():
  return "<h1>Blender Render Server V1.0"

@app.route("/getBlend", methods=['GET']) # serve blend file
def get_blend_file():
  return send_from_directory(ROOT_DIRECTORY,"render.blend")


@app.route("/Render.zip", methods=['GET']) # serve blend file
def get_rendered_files():
  os.system("rm images.zip")
  os.system("zip -r images.zip Images/")
  return send_from_directory(ROOT_DIRECTORY,"images.zip")

@app.route('/sendBlend', methods=['POST']) # get blend file from master
def recieve_blend_file():
  global framestorender
  for file in request.files:
    framerange = file.split("-")
    framestorender=list(range(int(framerange[0]),int(framerange[1])+1))
    request.files[file].save(ROOT_DIRECTORY+"render.blend")
  return "OK"

@app.route('/sendFrame', methods=['POST']) # get frame from client
def recieve_frame():
  for image in request.files:
    request.files[image].save(ROOT_DIRECTORY+"Images/"+image+".png")
  return "OK"

@app.route('/requestFrame', methods=['GET']) # sind a frame to a client
def distrubite_frame():
  if len(framestorender) > 0:
    responce = framestorender[0]
    del framestorender[0]
    return jsonify(responce)
  else:
    return jsonify(-1)




app.run(host='0.0.0.0', port=8080)
