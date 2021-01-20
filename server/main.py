import flask
import os
from flask import request, jsonify, send_from_directory, render_template
app = flask.Flask(__name__)
app.config["DEBUG"] = False


framestorender = []
unrenderedframes = 0
totalframes = 1
Version = None


ROOT_DIRECTORY = "/home/runner/BlenderRenderServer/"

@app.route('/', methods=['GET'])  # root page
def root():
    global unrenderedframes
    global totalframes
    return render_template('index.html', percent=str(int((unrenderedframes - totalframes) / totalframes *-100)))
    #return f"<head><link rel=\"stylesheet\" href=\"style/s.css\"></head><center><h1>Blender Render Server</h1>" + str(int((unrenderedframes - totalframes) / totalframes *-100)) + "% complete</center><br><small><a href=\"https://github.com/shrek231/Render-Home\">Github</a></small>"


@app.route("/style/<path:path>", methods=['GET'])  # serve blend file
def get_files(path):
    return send_from_directory(ROOT_DIRECTORY,  "style/" + path)

@app.route("/getBlend", methods=['GET'])  # serve blend file
def get_blend_file():
    return send_from_directory(ROOT_DIRECTORY, "render.blend")


@app.route("/cancel", methods=['GET'])  # serve blend file
def cancel_renders():
    global framestorender
    global unrenderedframes
    global totalframes
    totalframes = 1
    framestorender = []
    unrenderedframes = 0
    return "OK"


@app.route("/Render.zip", methods=['GET'])  # serve blend file
def get_rendered_files():
    os.system("rm images.zip")
    os.system("zip -r images.zip Images/")
    return send_from_directory(ROOT_DIRECTORY, "images.zip")


@app.route('/sendBlend', methods=['POST'])  # get blend file from master
def recieve_blend_file():
    global framestorender
    global unrenderedframes
    global totalframes
    global Version
    try:
      if request.form["Password"] != os.getenv("password"):
        return "Incorrect password"
    except:
      return "Password error"
    for file in request.files:
        framerange = file.split("-")
        framestorender = list(
            range(int(framerange[0]),
                  int(framerange[1]) + 1))
        unrenderedframes = len(framestorender)
        totalframes = len(framestorender)
        request.files[file].save(ROOT_DIRECTORY + "render.blend")
    os.system("rm Images/*")
    Version = request.form["Version"]
    return "OK"


@app.route('/sendFrame', methods=['POST'])  # get frame from client
def recieve_frame():
    global unrenderedframes
    for image in request.files:
        request.files[image].save(ROOT_DIRECTORY + "Images/" +
                                  f"{int(image):04}" + ".png")
        unrenderedframes = unrenderedframes - 1
    return "OK"


@app.route('/requestFrame', methods=['GET'])  # send a frame to a client
def distrubite_frame():
    if len(framestorender) > 0:
        responce = framestorender[0]
        del framestorender[0]
        return jsonify(responce)
    else:
        return jsonify(-1)


@app.route('/status', methods=['GET'])  # send a frame to a client
def render_status():
    return jsonify(unrenderedframes)


@app.route('/version', methods=['GET'])  # send a frame to a client
def blender_version():
    global Version
    return jsonify(Version)

@app.route('/cancelFrame',methods=['POST'])  # add a frame back into the frames to render
def cancel_render():
    global framestorender
    if int(request.json["frame"]) not in framestorender:
        framestorender.append(int(request.json["frame"]))
    return "OK"

if __name__ == "__main__":
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)