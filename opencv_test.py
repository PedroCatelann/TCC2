# Importar bibliotecas necessárias
import cv2
import numpy as np
from keras_retinanet import models
from keras_retinanet.utils.image import preprocess_image, resize_image

# Carregar o modelo pré-treinado
model_path = '/path/to/retinanet.h5'
model = models.load_model(model_path, backbone_name='resnet50')

# Definir classes dos objetos a serem detectados
class_names = ['classe_1', 'classe_2', 'classe_3', ...]

# Carregar imagem de entrada
image_path = '/path/to/image.jpg'
image = cv2.imread(image_path)

# Pré-processar imagem
image = preprocess_image(image)
image, scale = resize_image(image)

# Alimentar imagem no modelo e obter previsões
boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))

# Pós-processar previsões
boxes /= scale
threshold = 0.5
for box, score, label in zip(boxes[0], scores[0], labels[0]):
    if score < threshold:
        break
    color = label * 30 % 255
    box = box.astype(np.int32)
    cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, color, 0), 2)
    cv2.putText(image, f'{class_names[label]} {score:.3f}', (box[0], box[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, color, 0), 2)

# Exibir imagem de saída
cv2.imshow('Detecção de objetos', image)
cv2.waitKey(0)