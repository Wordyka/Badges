# -*- coding: utf-8 -*-
"""Copy of Semoga Berhasil.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EyLTvo_t9fGtyP6a2rizsu3ITMnxfGDe
"""

#Import Libraries
import tensorflow as tf
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.optimizers.legacy import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import models, layers
from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from sklearn import datasets
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import os


root_dir = '/TA-2/dataset/dataset'
training_dir = os.path.join(root_dir, 'train')
valid_dir = os.path.join(root_dir,'validation')
testing_dir = os.path.join(root_dir, 'test')

print(os.listdir(training_dir))
print(os.listdir(valid_dir))
print(os.listdir(testing_dir))

import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import random

# Path ke direktori dengan subfolder
training_subfolders = os.listdir(training_dir)

# Fungsi untuk menampilkan gambar dari setiap subfolder
def display_images_from_subfolders(subfolder):
    plt.figure(figsize=(15, 10))
    for i, folder in enumerate(subfolder):
        folder_path = os.path.join(training_dir, folder)
        image_list = os.listdir(folder_path)
        # Pilih satu gambar secara acak dari setiap subfolder
        image_name = random.choice(image_list)
        img_path = os.path.join(folder_path, image_name)
        img = mpimg.imread(img_path)
        plt.subplot(2, 3, i + 1)
        plt.imshow(img)
        plt.axis('off')
        plt.title(f'{folder} - {image_name}')
    plt.show()

# Menampilkan gambar dari setiap subfolder
display_images_from_subfolders(training_subfolders)

import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import random

# Path ke direktori dengan subfolder
valid_subfolders = os.listdir(valid_dir)

# Fungsi untuk menampilkan gambar dari setiap subfolder
def display_images_from_subfolders(subfolder):
    plt.figure(figsize=(15, 10))
    for i, folder in enumerate(subfolder):
        folder_path = os.path.join(valid_dir, folder)
        image_list = os.listdir(folder_path)
        # Pilih satu gambar secara acak dari setiap subfolder
        image_name = random.choice(image_list)
        img_path = os.path.join(folder_path, image_name)
        img = mpimg.imread(img_path)
        plt.subplot(2, 3, i + 1)
        plt.imshow(img)
        plt.axis('off')
        plt.title(f'{folder} - {image_name}')
    plt.show()

# Menampilkan gambar dari setiap subfolder
display_images_from_subfolders(training_subfolders)

train_datagen = ImageDataGenerator(
                    rescale=1./255,
                    rotation_range=20,
                    horizontal_flip=True,
                    width_shift_range = 0.2,
                    shear_range=0.2,
                    fill_mode='nearest')

valid_datagen = ImageDataGenerator(
                    rescale=1./255,
                    vertical_flip = True,
                    height_shift_range = 0.2)

train_generator = train_datagen.flow_from_directory(training_dir,
                                                    #batch_size = 6,
                                                    batch_size = 32,
                                                    target_size = (299, 299),
                                                    color_mode='rgb',
                                                    shuffle=True,
                                                    class_mode='categorical')

valid_generator =  valid_datagen.flow_from_directory(valid_dir,
                                                   #batch_size  = 6,
                                                   batch_size = 32,
                                                   target_size = (299, 299),
                                                   color_mode='rgb',
                                                   shuffle=True,
                                                   class_mode='categorical')

#base_model = InceptionV3(input_shape = (299, 299, 3),
#                                include_top = False,
#                                weights = 'imagenet')

# Define the number of classes
num_classes = 6  # Change this to your number of classes

from keras.models import Model
from keras.layers import concatenate
from keras.layers import Conv2D , MaxPool2D , Input , GlobalAveragePooling2D ,AveragePooling2D, Dense , Dropout ,Activation, Flatten , BatchNormalization


def conv_with_Batch_Normalisation(input_shape , nbr_kernels , filter_Size , strides =(1,1) , padding = 'same'):
    x = Conv2D(filters=nbr_kernels, kernel_size = filter_Size, strides=strides , padding=padding)(input_shape)
    x = BatchNormalization(axis=-1)(x)
    x = Activation(activation='relu')(x)
    return x


def StemBlock(input_shape):
    x = conv_with_Batch_Normalisation(input_shape, nbr_kernels = 32, filter_Size=(3,3) , strides=(2,2))
    x = conv_with_Batch_Normalisation(x, nbr_kernels = 32, filter_Size=(3,3))
    x = conv_with_Batch_Normalisation(x, nbr_kernels = 64, filter_Size=(3,3))
    x = MaxPool2D(pool_size=(3,3) , strides=(2,2)) (x)
    x = conv_with_Batch_Normalisation(x, nbr_kernels = 80, filter_Size=(1,1))
    x = conv_with_Batch_Normalisation(x, nbr_kernels = 192, filter_Size=(3,3))
    x = MaxPool2D(pool_size=(3,3) , strides=(2,2)) (x)

    return x


def InceptionBlock_A(input_shape  , nbr_kernels):

    branch1 = conv_with_Batch_Normalisation(input_shape, nbr_kernels = 64, filter_Size = (1,1))
    branch1 = conv_with_Batch_Normalisation(branch1, nbr_kernels=96, filter_Size=(3,3))
    branch1 = conv_with_Batch_Normalisation(branch1, nbr_kernels=96, filter_Size=(3,3))

    branch2 = conv_with_Batch_Normalisation(input_shape, nbr_kernels=48, filter_Size=(1,1))
    branch2 = conv_with_Batch_Normalisation(branch2, nbr_kernels=64, filter_Size=(3,3)) # may be 3*3

    branch3 = AveragePooling2D(pool_size=(3,3) , strides=(1,1) , padding='same') (input_shape)
    branch3 = conv_with_Batch_Normalisation(branch3, nbr_kernels = nbr_kernels, filter_Size = (1,1))

    branch4 = conv_with_Batch_Normalisation(input_shape, nbr_kernels=64, filter_Size=(1,1))

    output = concatenate([branch1 , branch2 , branch3 , branch4], axis=3)

    return output



def InceptionBlock_B(input_shape , nbr_kernels):

    branch1 = conv_with_Batch_Normalisation(input_shape, nbr_kernels = nbr_kernels, filter_Size = (1,1))
    branch1 = conv_with_Batch_Normalisation(branch1, nbr_kernels = nbr_kernels, filter_Size = (7,1))
    branch1 = conv_with_Batch_Normalisation(branch1, nbr_kernels = nbr_kernels, filter_Size = (1,7))
    branch1 = conv_with_Batch_Normalisation(branch1, nbr_kernels = nbr_kernels, filter_Size = (7,1))
    branch1 = conv_with_Batch_Normalisation(branch1, nbr_kernels = 192, filter_Size = (1,7))

    branch2 = conv_with_Batch_Normalisation(input_shape, nbr_kernels = nbr_kernels, filter_Size = (1,1))
    branch2 = conv_with_Batch_Normalisation(branch2, nbr_kernels = nbr_kernels, filter_Size = (1,7))
    branch2 = conv_with_Batch_Normalisation(branch2, nbr_kernels = 192, filter_Size = (7,1))

    branch3 = AveragePooling2D(pool_size=(3,3) , strides=(1,1) , padding ='same') (input_shape)
    branch3 = conv_with_Batch_Normalisation(branch3, nbr_kernels = 192, filter_Size = (1,1))

    branch4 = conv_with_Batch_Normalisation(input_shape, nbr_kernels = 192, filter_Size = (1,1))

    output = concatenate([branch1 , branch2 , branch3 , branch4], axis = 3)

    return output

def InceptionBlock_C(input_shape):

    branch1 = conv_with_Batch_Normalisation(input_shape, nbr_kernels = 448, filter_Size = (1,1))
    branch1 = conv_with_Batch_Normalisation(branch1, nbr_kernels = 384, filter_Size = (3,3))
    branch1_1 = conv_with_Batch_Normalisation(branch1, nbr_kernels = 384, filter_Size = (1,3))
    branch1_2 = conv_with_Batch_Normalisation(branch1, nbr_kernels = 384, filter_Size = (3,1))
    branch1 = concatenate([branch1_1 , branch1_2], axis = 3)

    branch2 = conv_with_Batch_Normalisation(input_shape, nbr_kernels = 384, filter_Size = (1,1))
    branch2_1 = conv_with_Batch_Normalisation(branch2, nbr_kernels = 384, filter_Size = (1,3))
    branch2_2 = conv_with_Batch_Normalisation(branch2, nbr_kernels = 384, filter_Size = (3,1))
    branch2 = concatenate([branch2_1 , branch2_2], axis = 3)

    branch3 = AveragePooling2D(pool_size=(3,3) , strides=(1,1) , padding='same')(input_shape)
    branch3 = conv_with_Batch_Normalisation(branch3, nbr_kernels = 192, filter_Size = (1,1))

    branch4 = conv_with_Batch_Normalisation(input_shape, nbr_kernels = 320, filter_Size = (1,1))

    output = concatenate([branch1 , branch2 , branch3 , branch4], axis = 3)

    return output


def ReductionBlock_A(input_shape):

    branch1 = conv_with_Batch_Normalisation(input_shape, nbr_kernels = 64, filter_Size = (1,1))
    branch1 = conv_with_Batch_Normalisation(branch1, nbr_kernels = 96, filter_Size = (3,3))
    branch1 = conv_with_Batch_Normalisation(branch1, nbr_kernels = 96, filter_Size = (3,3) , strides=(2,2) ) #, padding='valid'

    branch2 = conv_with_Batch_Normalisation(input_shape, nbr_kernels = 384, filter_Size=(3,3) , strides=(2,2) )

    branch3 = MaxPool2D(pool_size=(3,3) , strides=(2,2) , padding='same')(input_shape)

    output = concatenate([branch1 , branch2 , branch3], axis = 3)

    return output


def ReductionBlock_B(input_shape):

    branch1 = conv_with_Batch_Normalisation(input_shape, nbr_kernels = 192, filter_Size = (1,1))
    branch1 = conv_with_Batch_Normalisation(branch1, nbr_kernels = 192, filter_Size = (1,7))
    branch1 = conv_with_Batch_Normalisation(branch1, nbr_kernels = 192, filter_Size = (7,1))
    branch1 = conv_with_Batch_Normalisation(branch1, nbr_kernels = 192, filter_Size = (3,3) , strides=(2,2) , padding = 'valid')

    branch2 = conv_with_Batch_Normalisation(input_shape, nbr_kernels = 192, filter_Size = (1,1) )
    branch2 = conv_with_Batch_Normalisation(branch2, nbr_kernels = 320, filter_Size = (3,3) , strides=(2,2) , padding='valid' )

    branch3 = MaxPool2D(pool_size=(3,3) , strides=(2,2) )(input_shape)

    output = concatenate([branch1 , branch2 , branch3], axis = 3)

    return output


########################
def auxiliary_classifier(input_shape, num_classes):
    x = AveragePooling2D(pool_size=(5, 5), strides=(3, 3))(input_shape)
    x = conv_with_Batch_Normalisation(x, nbr_kernels=128, filter_Size=(1, 1))
    x = Flatten()(x)
    x = Dropout(rate=0.2)(x)
    #x = Conv2D(num_classes, (1, 1), activation='softmax')(x)
    x = Dense(units=num_classes, activation='softmax')(x)
    return x


from keras.layers import Reshape

def auxiliary_classifier(input_shape, num_classes):
    x = AveragePooling2D(pool_size=(5, 5), strides=(3, 3))(input_shape)
    x = conv_with_Batch_Normalisation(x, nbr_kernels=128, filter_Size=(1, 1))
    x = GlobalAveragePooling2D()(x)  # Menggunakan GlobalAveragePooling2D untuk mengurangi dimensi
    x = Flatten()(x)
    x = Dropout(rate=0.2)(x)
    x = Reshape((1, 1, 128))(x)  # Konversi output menjadi tensor 4 dimensi
    x = Conv2D(num_classes, (1, 1), activation='softmax')(x)
    return x


def InceptionV3(num_classes):

    input_shape = Input(shape=(299 , 299 , 3))

    x = StemBlock(input_shape)

    x = InceptionBlock_A(input_shape=x, nbr_kernels=32)
    x = InceptionBlock_A(input_shape=x, nbr_kernels=64)
    x = InceptionBlock_A(input_shape=x, nbr_kernels=64)

    x = ReductionBlock_A(input_shape=x)
    x = Dropout(rate=0.3)(x)

    x = InceptionBlock_B(input_shape=x, nbr_kernels=128)
    x = InceptionBlock_B(input_shape=x, nbr_kernels=160)
    x = InceptionBlock_B(input_shape=x, nbr_kernels=160)
    x = InceptionBlock_B(input_shape=x, nbr_kernels=192)

    x = ReductionBlock_B(input_shape=x)
    x = Dropout(rate=0.3)(x)

    x = InceptionBlock_C(input_shape=x)
    x = InceptionBlock_C(input_shape=x)

    x = GlobalAveragePooling2D()(x)
    x = Flatten()(x)
    x = Dropout(rate=0.5)(x)
    x = Dense(units=num_classes, activation='softmax')(x)

    model = Model(inputs=input_shape, outputs=x, name='Inception-V3')

    # Compile the model
    #model.compile(optimizer=Adam(lr=0.001),
     #             loss='categorical_crossentropy',
      #            metrics=['accuracy'])

    #model.compile(optimizer=Adam(lr=0.01),
     #             loss='categorical_crossentropy',
      #            metrics=['accuracy'])

    model.compile(optimizer=Adam(lr=0.0001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    return model

from keras.models import load_model

model = InceptionV3(num_classes)

model.summary()

history = model.fit(
    train_generator,
    steps_per_epoch=15,
    epochs=25,
    workers=8,
    validation_data=valid_generator,
    validation_steps=8,
    verbose=1)