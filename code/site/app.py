from __future__ import division, print_function

import os
import json
import cv2
from PIL import Image
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')

def generate_audio(filepath):
    filename = filepath.split("\\")[-1]
    filepath = "/".join([".","uploads",filename]) 
    os.system("python ../wav2png.py --filename {} --mode single".format(filepath))
    print("----------Converted Uploaded Audio to Image----------")


    filepath = ".".join(filepath.split(".")[:-1]) + ".png"
    img = Image.open(filepath)    
    lwinfo = json.loads(img.text['meta'])
    minx, maxx = lwinfo['scaleMin'], lwinfo['scaleMax']

    im = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    im = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)
    cv2.imwrite(filepath, im)
    w = im.shape[0]
    h = im.shape[1]
    print("----------Converted GrayScale Image to RGB Image----------")


    os.system("python ../cycle_gan/test_image.py --file {} --model-name ../cycle_gan/weights/netG_A2B.pth".format(filepath))
    print("--------------Generated the Image--------------")


    im = cv2.imread("./result.png", cv2.COLOR_BGR2RGB)
    im = cv2.resize(im, (h,w))
    cv2.imwrite("./uploads/gen_image_resized.png", im)
    print("--------------Resized the Generated Image--------------")


    os.system("python ../png2wav.py --filename ./uploads/gen_image_resized.png --wavfile ./static/gen_audio.wav --scalemin {} --scalemax {}".format(minx, maxx))
    print("--------------Converted Generated Image to Audio--------------")

    return "/static/gen_audio.wav"


@app.route('/predict', methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        f = request.files["thefile"]
        if f:
            filename = secure_filename(f.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(filepath)
            result = generate_audio(filepath)
        else:
            result = {"pred": "null"}
        return result
    return None


if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)
