from __future__ import print_function
import keras
from keras.preprocessing.image import load_img
from keras.preprocessing.image import save_img
from keras.preprocessing.image import img_to_array
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, BatchNormalization
from keras.layers import Conv2D, MaxPooling2D
from keras.models import load_model
import keras.regularizers as Regularizers
import numpy as np
from sklearn.model_selection import train_test_split
import os
import matplotlib.pyplot as plt
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

original_parasitized = "C:\\Users\\reach\\Documents\\Stuff\\Machine Learning\\Malaria-Detector\\original_cell_images\\Parasitized\\"
original_uninfected = "C:\\Users\\reach\\Documents\\Stuff\\Machine Learning\\Malaria-Detector\\original_cell_images\\Uninfected\\"
resized_parasitized = "C:\\Users\\reach\\Documents\\Stuff\\Machine Learning\\Malaria-Detector\\resized_cell_images\\Parasitized\\"
resized_uninfected = "C:\\Users\\reach\\Documents\\Stuff\\Machine Learning\\Malaria-Detector\\resized_cell_images\\Uninfected\\"
original_images = "C:\\Users\\reach\\Documents\\Stuff\\Machine Learning\\Malaria-Detector\\original_cell_images\\"
resized_images = "C:\\Users\\reach\\Documents\\Stuff\\Machine Learning\\Malaria-Detector\\resized_cell_images\\"

batch_size, num_classes, epochs = 128, 2, 20
channels, img_rows, img_cols = 3, 38, 38
num_parasitized_images, num_uninfected_images = 13779, 13779
global num_parasitized_training, num_uninfected_training, num_parasitized_test, num_uninfected_test

global data, labels, data_train, data_test, labels_train, labels_test, input_shape

def resize_images():
	image_count = 0
	for filename in os.listdir(original_parasitized):
		if filename != "Thumbs.db":
			img = load_img(original_parasitized + filename, target_size=(img_rows, img_cols))
			img_array = img_to_array(img)
			save_img(resized_parasitized + filename, img_array)
			image_count += 1
			if image_count % 1000 == 0:
				print("Resizing parasitized cell image " + str(image_count))

	print("Finished resizing parasitized cell images")

	for filename in os.listdir(original_uninfected):
		if filename != "Thumbs.db":
			img = load_img(original_uninfected + filename, target_size=(img_rows, img_cols))
			img_array = img_to_array(img)
			save_img(resized_uninfected + filename, img_array)
			image_count += 1
			if (image_count - num_parasitized_images) % 1000 == 0:
				print("Resizing uninfected image " + str(image_count - num_parasitized_images))

	print("Finished resizing uninfected cell images")

def get_data():
	global data, labels

	if input("Load saved shuffled image data and labels?\n") in ["Yes", "yes"]:
		data, labels = np.load("data.npy"), np.load("labels.npy")
		print("Shuffled image data and labels loaded from data.npy and labels.npy")

	else:
		if input("Resize images?\n") in ["Yes", "yes"]:
			resize_images()

		data = np.ndarray(shape=(num_parasitized_images + num_uninfected_images, img_rows, img_cols, channels), dtype=np.float32)
		image_count = 0
		for filename in os.listdir(resized_parasitized):
			img = load_img(resized_parasitized + filename)
			img_array = img_to_array(img)
			img_array.reshape((img_rows, img_cols, channels))
			data[image_count] = img_array
			image_count += 1
			if image_count % 1000 == 0:
				print("Gathering parasitized cell image " + str(image_count))

		print("Finished gathering parasitized cell images data")

		for filename in os.listdir(resized_uninfected):
			img = load_img(resized_uninfected + filename)
			img_array = img_to_array(img)
			img_array.reshape((img_rows, img_cols, channels))
			data[image_count] = img_array
			image_count += 1
			if (image_count - num_parasitized_images) % 1000 == 0:
				print("Gathering uninfected image " + str(image_count - num_parasitized_images))

		print("Finished gathering uninfected cell images data")

		labels = np.ndarray(shape = (num_parasitized_images + num_uninfected_images), dtype = int)
		for n in range(0, num_parasitized_images):
			labels[n] = 1
		for n in range(num_parasitized_images, num_parasitized_images + num_uninfected_images):
			labels[n] = 0
		print("Generated labels")

		labels = keras.utils.to_categorical(labels, num_classes)
		print("One-hot encoded labels")

		idx = np.random.permutation(len(data))
		data, labels = data[idx], labels[idx]
		print("Shuffled data and labels")	

		if input("Save shuffled image data and labels?\n") in ["Yes", "yes"]:
			np.save(file = "data", arr = data)
			np.save(file = "labels", arr = labels)
			print("Shuffled image data and labels saved in data.npy and labels.npy")

def create_datasets(test_proportion):
	global data, labels, data_train, data_test, labels_train, labels_test, input_shape
	global num_parasitized_training, num_uninfected_training, num_parasitized_test, num_uninfected_test

	input_shape = (img_rows, img_cols, 3)

	load_sets = input("Load shuffled training and test sets?\n")
	if load_sets in ["Yes", "yes"]:
		data_train, data_test, labels_train, labels_test = np.load("data_train.npy"), np.load("data_test.npy"), np.load("labels_train.npy"), np.load("labels_test.npy")
		print("Loaded shuffled training and test sets")

	else:
		data_train, data_test, labels_train, labels_test = train_test_split(data, labels, test_size = test_proportion)
		
		data_train /= 255
		data_test /= 255
		print("Split and normalized shuffled data")
		
		if input("Save split and normalized shuffled data?\n") in ["Yes", "yes"]:
			np.save(file = "data_train.npy", arr = data_train)
			np.save(file = "data_test.npy", arr = data_test)
			np.save(file = "labels_train.npy", arr = labels_train)
			np.save(file = "labels_test.npy", arr = labels_test)
			print("Split and normalized shuffled data saved in data_train.npy, data_test.npy, labels_train.npy, and labels_test.npy")

	num_parasitized_training, num_uninfected_training, num_parasitized_test, num_uninfected_test = 0, 0, 0, 0

	for label in labels_train:
		if label[0] == np.float32(0):
			num_parasitized_training += 1
		else:
			num_uninfected_training += 1

	for label in labels_test:
		if label[0] == np.float32(0):
			num_parasitized_test += 1
		else:
			num_uninfected_test += 1

	print("Training set: " + str(num_parasitized_training / len(labels_train) * 100) + " percent parasitized, " + str(num_uninfected_training / len(labels_train) * 100) + " percent uninfected")
	print("Test set: " + str(num_parasitized_test / len(labels_test) * 100) + " percent parasitized, " + str(num_uninfected_test / len(labels_test) * 100) + " percent uninfected")

def train_model(input_shape):
	model = Sequential()
	model.add(Conv2D(38, kernel_size = (3, 3), activation = "relu", input_shape = input_shape))
	model.add(MaxPooling2D(pool_size = (2, 2)))
	model.add(Dropout(0.1))
	model.add(BatchNormalization())

	model.add(Conv2D(18, kernel_size = (3, 3), activation = "relu"))
	model.add(BatchNormalization())
	
	model.add(Conv2D(16, kernel_size = (3, 3), activation = "relu"))
	model.add(MaxPooling2D(pool_size = (2, 2)))
	model.add(BatchNormalization())
	
	model.add(Conv2D(7, kernel_size = (3, 3), activation = "relu"))
	model.add(BatchNormalization())
	
	model.add(Conv2D(5, kernel_size = (3, 3), activation = "relu"))
	model.add(MaxPooling2D(pool_size = (2, 2)))
	model.add(BatchNormalization())
	
	model.add(Flatten())
	model.add(Dense(128, activation = "relu"))
	model.add(Dropout(0.4))
	model.add(Dense(num_classes, activation = "softmax"))
	model.compile(loss = keras.losses.categorical_crossentropy, optimizer = keras.optimizers.Adadelta(), metrics = ["accuracy"])
	print("Created CNN model")

	history = model.fit(data_train, labels_train, batch_size = batch_size, epochs = epochs, verbose = 1)
	print("Finished training CNN model")

	return model, history
	
def save_cnn(model, filename):
	model.save(filename)
	print("Model saved as " + filename)

def load_cnn(filename):
	model = load_model(filename)
	print(filename + " loaded")
	return model

get_data()

load_name = input("Model to load?\n") + ".h5"
if load_name not in ["None.h5", "none.h5"]:
	model = load_cnn(load_name[0:len(load_name) - 3] + "\\" + load_name)
	create_datasets(test_proportion = 0.5)
	parasitized_test_data = np.ndarray(shape=(num_parasitized_images, img_rows, img_cols, channels), dtype=np.float32)
	uninfected_test_data = np.ndarray(shape=(num_uninfected_images, img_rows, img_cols, channels), dtype=np.float32)
	parasitized_test_labels = labels = np.ndarray(shape = (num_parasitized_images), dtype = int)
	uninfected_test_labels = labels = np.ndarray(shape = (num_uninfected_images), dtype = int)
	parasitized_counter, uninfected_counter = 0, 0
	for n in range(len(labels_test)):
		if labels_test[n][0] == np.float32(0):
			parasitized_test_labels[parasitized_counter] = 1
			parasitized_test_data[parasitized_counter] = data_test[n]
			parasitized_counter += 1
		else:
			uninfected_test_labels[uninfected_counter] = 0
			uninfected_test_data[uninfected_counter] = data_test[n]
			uninfected_counter += 1
	parasitized_test_labels = keras.utils.to_categorical(parasitized_test_labels, num_classes)
	uninfected_test_labels = keras.utils.to_categorical(uninfected_test_labels, num_classes)
	print("Split test set into parasitized and uninfected image data and labels")
	score_parasitized = model.test_on_batch(parasitized_test_data, parasitized_test_labels)
	print("Accuracy on parasitized images: " + str(score_parasitized[1]))
	score_uninfected = model.test_on_batch(uninfected_test_data, uninfected_test_labels)
	print("Accuracy on uninfected images: " + str(score_uninfected[1]))
	score = model.test_on_batch(data_test, labels_test)
	print("Accuracy on all images: " + str(score[1]))
	
if input("Train new model?\n") in ["Yes", "yes"]:
	create_datasets(float(input("Proportion of data to enter into test set?\n")))
	model, history = train_model(input_shape)
	score = model.evaluate(data_test, labels_test, verbose = 1)
	print("Test loss: ", score[0])
	print("Test accuracy: ", score[1])

	plt.plot(history.history["acc"])
	plt.title("Model accuracy")
	plt.ylabel("Accuracy")
	plt.xlabel("Epoch")
	plt.show()
	
	if input("Save the model?\n") in ["Yes", "yes"]:
		save_cnn(model = model, filename = input("Filename to save the model with?\n") + ".h5")



