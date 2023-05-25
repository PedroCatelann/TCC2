import cv2
import numpy as np
import torchvision
from torchvision.io.image import read_image
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image
from torchvision.models.detection import retinanet_resnet50_fpn_v2, RetinaNet_ResNet50_FPN_V2_Weights
from PIL import Image, ImageDraw
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import shutil
import requests
def detect(i):
    response = requests.get('https://i.ytimg.com/vi/q71MCWAEfL8/maxresdefault.jpg')
    img = Image.open('A.jpg').convert('RGB')
    print(np.array(img).shape)

    weights = RetinaNet_ResNet50_FPN_V2_Weights.DEFAULT
    model = retinanet_resnet50_fpn_v2(weights=weights, score_thresh=0.35)
    # Put the model in inference mode
    model.eval()
    # Get the transforms for the model's weights
    preprocess = weights.transforms()

    batch = [preprocess(img)]
    prediction = model(batch)[0]
    transform = transforms.Compose([
        transforms.PILToTensor()
    ])
    
    # transform = transforms.PILToTensor()
    # Convert the PIL image to Torch tensor
    img = transform(img)
    labels = [weights.meta["categories"][i] for i in prediction["labels"]]
    print('='*50)

    print(len(prediction["labels"]))
    print('='*50)

    transform = transforms.Compose([transforms.PILToTensor()])

    box = draw_bounding_boxes(img, boxes=prediction["boxes"],labels=labels,
                            colors="cyan",
                            width=2, 
                            font_size=30,
                            font='arial.ttf')

    im = to_pil_image(box.detach())

    fig, ax = plt.subplots(figsize=(16, 12))
    numpydata = np.array(im)
 
    # ax.imshow(im)
    cv2.imwrite("static/r.jpg", numpydata)
    print("labels: " + str(prediction["labels"]))
    retina_num = 0
    for i in prediction["labels"]:
        if i == 21:
            retina_num = retina_num + 1
    # cv2.imwrite("C:/Users/pedro/OneDrive/Ambiente de Trabalho/r.jpg", numpydata)

    return retina_num
    # plt.show()