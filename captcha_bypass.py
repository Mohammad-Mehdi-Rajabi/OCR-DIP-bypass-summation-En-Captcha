import cv2 
import numpy as np
import easyocr
import re
import urllib.request
from flask import Flask, render_template, request, Response, jsonify


app = Flask(__name__)

def fetch_image(url):
    with urllib.request.urlopen(url) as response:
        image_data = response.read()
    return image_data
def bypass(img):
  try:
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY +  cv2.THRESH_OTSU)
    kernel_size = (2, 2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    img = cv2.bitwise_not(img)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, kernel_size)
    img = cv2.erode(img, kernel, iterations=1)
    reader = easyocr.Reader(['en'], gpu=False, verbose=True)
    cv2.imshow("n",img)
    cv2.waitKey(0)
    results = reader.readtext(img)
    numbers = []
    for (bbox, text, score) in results:
        # somethimes detect 2 -> Z or z
        text = text.replace('Z', '2').replace('z', '2')
        # print(f"Text: {text}, Score: {score}")
        numbers.append(re.findall(r'/d+', text))
        # print(numbers)
    if len(numbers) == 1:
      # check if first num or sec. was more than 2 digit -> delete index>=2
      if len(numbers[0][0])>2:
        numbers[0][0] =numbers[0][0][0:2]
      if len(numbers[0][1])>2: 
        numbers[0][1] =numbers[0][1][0:2]
      return (int(numbers[0][0])+(int(numbers[0][1])))
    elif len(numbers) == 2:
      # check if first num or sec. was more than 2 digit -> delete index>=2
      if len(numbers[0][0])>2:
        numbers[0][0] =numbers[0][0][0:2]
      if len(numbers[1][0])>2: 
        numbers[1][0] =numbers[1][0][0:2]
      return (int(numbers[0][0])+(int(numbers[1][0])))
    else :
      return 0
  except Exception as e:
    print(e)


@app.route('/bypass', methods=['POST'])
def process():
    data = request.get_json()
    # todo parse jsone to get url
    image_url = data['url']
    image_data = fetch_image(image_url)
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    res = bypass(image)
    response = {
        "result": res
    }
    return jsonify(response)
    
    
    
if __name__ == '__main__':
    app.run()



