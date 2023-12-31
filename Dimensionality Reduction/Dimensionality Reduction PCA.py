# -*- coding: utf-8 -*-
"""MLBD_Ass3_m22ma003Q2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1r-4dPfHF8fsXodNLh-_0h4swRJd-vwFO
"""

import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
from sklearn.decomposition import PCA
import time

# Load the MNIST dataset
train_dataset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transforms.ToTensor())
test_dataset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transforms.ToTensor())

# Define a function to apply PCA on the dataset
def apply_pca(data, n_components):
    data = data.reshape(data.shape[0], -1)
    pca = PCA(n_components=n_components)
    pca.fit(data)
    transformed_data = pca.transform(data)
    return transformed_data.reshape(data.shape[0], -1)

# Apply PCA on the dataset
n_components = 200
train_data_pca = apply_pca(train_dataset.data.numpy(), n_components)
test_data_pca = apply_pca(test_dataset.data.numpy(), n_components)

# Create a new dataset with reduced dimensions
class ReducedMNISTDataset(torch.utils.data.Dataset):
    def __init__(self, data, targets):
        self.data = torch.from_numpy(data).float()
        self.targets = torch.from_numpy(targets).long()

    def __getitem__(self, index):
        return self.data[index], self.targets[index]

    def __len__(self):
        return len(self.data)

train_dataset_pca = ReducedMNISTDataset(train_data_pca, train_dataset.targets.numpy())
test_dataset_pca = ReducedMNISTDataset(test_data_pca, test_dataset.targets.numpy())

print(type(train_dataset_pca))
print(type(test_dataset_pca))
class NaiveBayes(nn.Module):
    def __init__(self, num_features, num_classes):
        super(NaiveBayes, self).__init__()
        self.num_features = num_features
        self.num_classes = num_classes
        self.theta = nn.Parameter(torch.randn(num_classes, num_features))
        self.log_prior = nn.Parameter(torch.zeros(num_classes))
        
    def forward(self, x):
        log_probs = torch.matmul(x.view(-1, self.num_features), self.theta.t()) + self.log_prior
        return log_probs
    
    def update(self, x, y):
        class_counts = torch.zeros(self.num_classes)
        feature_counts = torch.zeros(self.num_classes, self.num_features)
        # print(x[0, :].view(1,-1).squeeze().shape)
        # print(x.shape, class_counts.shape, feature_counts.shape)
        for i in range(x.shape[0]):
            class_counts[y[i]] += 1
            feature_counts[y[i], :] += x[i, :].view(1, -1).squeeze()
        
        self.theta.data = feature_counts / class_counts.view(-1, 1)
        self.log_prior.data = torch.log(class_counts / class_counts.sum())


# Define the model
# class NaiveBayes(nn.Module):
#     def __init__(self, num_classes, num_features):
#         super(NaiveBayes, self).__init__()
#         self.num_classes = num_classes
#         self.num_features = num_features
#         self.theta = nn.Parameter(torch.zeros(num_classes, num_features))
#         self.sigma = nn.Parameter(torch.ones(num_classes, num_features))

#     def forward(self, x):
#         log_prob = torch.log_softmax(torch.exp(self.theta) / torch.exp(self.sigma) * x.unsqueeze(1) - self.theta.pow(2) / (2 * self.sigma.pow(2)).log().sum(-1), dim=1)
#         return log_prob.sum(1)

# Train the model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
batch_size = 128
learning_rate = 0.001
num_epochs = 5
train_loader = torch.utils.data.DataLoader(train_dataset_pca, batch_size=batch_size, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset_pca, batch_size=batch_size, shuffle=False)


model = NaiveBayes(num_classes=10, num_features=n_components).to(device)
criterion = nn.NLLLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
pred_data=[]
start_time = time.time()
# Train model
for epoch in range(num_epochs):
    for i, (images, labels) in enumerate(train_loader):
        # Flatten images into a 784-dimensional vector
        images = images.view(-1, 200)
        
        # Compute log probabilities and loss
        log_probs = model(images)
        loss = nn.functional.nll_loss(log_probs, labels)
        
        # Zero gradients, perform backward pass, and update parameters
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Update model parameters with new data
        model.update(images, labels)
        
        # Print progress
        if (i+1) % 100 == 0:
            print('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}'.format(epoch+1, num_epochs, i+1, len(train_loader), loss.item()/len(train_loader)))
end_time = time.time()
training_time = end_time - start_time
# Test model
start_time = time.time()
with torch.no_grad():
    correct = 0
    total = 0
    
    for images, labels in test_loader:
        # Flatten images into a 784-dimensional vector
        images = images.view(-1, 200)
        
        # Compute log probabilities and predicted labels
        log_probs = model(images)
        _, predicted = torch.max(log_probs.data, 1)
        pred_data.append(predicted)
        # Update counts of correct and total predictions
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

        
    # Print accuracy
    print('Test Accuracy of the model on the 10000 test images: {} %'.format(100 * correct / total))
    end_time = time.time()
    testing_time = end_time - start_time
    print(f"Training and testing time are:{training_time:.4f} and {testing_time:.4f}")

len(pred_data)*128

print(f"Classification on the test set for n_dimension = 200 are:\n{pred_data}")

"""No of dimensions =500"""

n_components = 500
train_data_pca = apply_pca(train_dataset.data.numpy(), n_components)
test_data_pca = apply_pca(test_dataset.data.numpy(), n_components)
train_dataset_pca = ReducedMNISTDataset(train_data_pca, train_dataset.targets.numpy())
test_dataset_pca = ReducedMNISTDataset(test_data_pca, test_dataset.targets.numpy())




# Train the model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
batch_size = 128
learning_rate = 0.001
num_epochs = 5
train_loader = torch.utils.data.DataLoader(train_dataset_pca, batch_size=batch_size, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset_pca, batch_size=batch_size, shuffle=False)


model1 = NaiveBayes(num_classes=10, num_features=n_components).to(device)
criterion = nn.NLLLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
pred_data1=[]
start_time = time.time()
# Train model
for epoch in range(num_epochs):
    for i, (images, labels) in enumerate(train_loader):
        # Flatten images into a 784-dimensional vector
        images = images.view(-1, 500)
        
        # Compute log probabilities and loss
        log_probs = model1(images)
        loss = nn.functional.nll_loss(log_probs, labels)
        
        # Zero gradients, perform backward pass, and update parameters
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Update model parameters with new data
        model1.update(images, labels)
        
        # Print progress
        if (i+1) % 100 == 0:
            print('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}'.format(epoch+1, num_epochs, i+1, len(train_loader), loss.item()/len(train_loader)))
end_time = time.time()
training_time = end_time - start_time
# Test model
start_time = time.time()
with torch.no_grad():
    correct = 0
    total = 0
    
    for images, labels in test_loader:
        # Flatten images into a 784-dimensional vector
        images = images.view(-1, 200)
        
        # Compute log probabilities and predicted labels
        log_probs = model1(images)
        _, predicted = torch.max(log_probs.data, 1)
        pred_data1.append(predicted)

        # Update counts of correct and total predictions
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
    # Print accuracy
    print('Test Accuracy of the model on the 10000 test images: {} %'.format(100 * correct / total))
    end_time = time.time()
    testing_time = end_time - start_time
    print(f"Training and testing time are:{training_time:.4f} and {testing_time:.4f}")

print(f"Classification on the test set for n_dimension = 500 are:\n{pred_data1}")

"""No of dimensions =100"""

n_components = 100
train_data_pca = apply_pca(train_dataset.data.numpy(), n_components)
test_data_pca = apply_pca(test_dataset.data.numpy(), n_components)
train_dataset_pca = ReducedMNISTDataset(train_data_pca, train_dataset.targets.numpy())
test_dataset_pca = ReducedMNISTDataset(test_data_pca, test_dataset.targets.numpy())




# Train the model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
batch_size = 128
learning_rate = 0.001
num_epochs = 5
train_loader = torch.utils.data.DataLoader(train_dataset_pca, batch_size=batch_size, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset_pca, batch_size=batch_size, shuffle=False)


model1 = NaiveBayes(num_classes=10, num_features=n_components).to(device)
criterion = nn.NLLLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
pred_data1=[]
start_time = time.time()
# Train model
for epoch in range(num_epochs):
    for i, (images, labels) in enumerate(train_loader):
        # Flatten images into a 784-dimensional vector
        images = images.view(-1, 100)
        
        # Compute log probabilities and loss
        log_probs = model1(images)
        loss = nn.functional.nll_loss(log_probs, labels)
        
        # Zero gradients, perform backward pass, and update parameters
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Update model parameters with new data
        model1.update(images, labels)
        
        # Print progress
        if (i+1) % 100 == 0:
            print('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}'.format(epoch+1, num_epochs, i+1, len(train_loader), loss.item()/len(train_loader)))
end_time = time.time()
training_time = end_time - start_time
# Test model
start_time = time.time()
with torch.no_grad():
    correct = 0
    total = 0
    
    for images, labels in test_loader:
        # Flatten images into a 784-dimensional vector
        images = images.view(-1, 200)
        
        # Compute log probabilities and predicted labels
        log_probs = model1(images)
        _, predicted = torch.max(log_probs.data, 1)
        pred_data1.append(predicted)

        # Update counts of correct and total predictions
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
    # Print accuracy
    print('Test Accuracy of the model on the 10000 test images: {} %'.format(100 * correct / total))
    end_time = time.time()
    testing_time = end_time - start_time
    print(f"Training and testing time are:{training_time:.4f} and {testing_time:.4f}")

print(f"Classification on the test set for n_dimension = 100 are:\n{pred_data1}")

"""Method 2 for implementation """

import numpy as np
# import psutil
import warnings
warnings.filterwarnings('ignore')
from matplotlib import pyplot as plt
from keras.datasets import mnist
# from datasketch import MinHash, MinHashLSH
import time

import numpy as np
from keras.datasets import mnist
(X_train_data, y_train_data), (X_test_data, y_test_data) = mnist.load_data()
X_train = X_train_data.reshape(-1, 28*28)[:60000]
y_train = y_train_data[:60000]
X_test = X_test_data.reshape(-1, 28*28)[:10000]
y_test = y_test_data[:10000]

#converting the values in the binary
X_train=np.where(X_train>105,1,0)
X_test=np.where(X_test>105,1,0)
# x_test.ndim

import numpy as np
y_pred=[]
class StreamNBayes:
    def __init__(self, num_features, num_classes):
        self.num_features = num_features
        self.num_classes = num_classes
        self.counts = np.zeros((num_classes, num_features))
        self.class_counts = np.zeros(num_classes)
    
    def update(self, X, y):
        self.counts[y] += X
        self.class_counts[y] += 1
        
    def predict(self, X):
        probs = np.zeros(self.num_classes)
        for c in range(self.num_classes):
            feat_probs = (self.counts[c] + 1) / (self.class_counts[c] + 2)
            probs[c] = np.sum(X * np.log(feat_probs) + (1 - X) * np.log(1 - feat_probs))
        y_pred.append((np.argmax(probs)))
        return np.argmax(probs)



n_components = 100

# Here, we'll use PCA as an example
pca = PCA(n_components= 100)
X_train_red = apply_pca(X_train, n_components)
X_test_red = apply_pca(X_test, n_components)

def naive_b(X_train, y_train, X_test, y_test, num_features):
    n_b = StreamNBayes(num_features, 10)
    start_time = time.time()
    for i in range(X_train.shape[0]):
        n_b.update(X_train[i], y_train[i])
    end_time = time.time()
    training_time = end_time - start_time
    start_time = time.time()
    correct = 0
    for i in range(X_test.shape[0]):
        pred = n_b.predict(X_test[i])
        if pred == y_test[i]:
            correct += 1
    accuracy = correct / X_test.shape[0]

    end_time = time.time()
    testing_time = end_time - start_time
    print(f"Training and testing time are:{training_time:.4f} and {testing_time:.4f}")
    return accuracy

accuracy = (naive_b(X_train_red, y_train, X_test_red, y_test, 100))
print(f"Accuracy of 100 dimension MNIST dataset using NB algo:-{(accuracy*100):.4f} %")

n_b = StreamNBayes(n_components, 10)
for i in range(X_test_red.shape[0]):
    pred = n_b.predict(X_test_red[i])
print(y_test)

# Here, we'll use PCA as an example
n_components= 200
pca = PCA(n_components= 200)
# X_train_red = pca.transform(X_train)
# X_test_red = pca.transform(X_test)
X_train_red = apply_pca(X_train, n_components)
X_test_red = apply_pca(X_test, n_components)

accuracy = (naive_b(X_train_red, y_train, X_test_red, y_test, 200))
print(f"Accuracy of 200 dimension MNIST dataset using NB algo:-{(accuracy*100):.4f} %")
print(y_test)

# Here, we'll use PCA as an example
n_components= 500
pca = PCA(n_components= 200)
# X_train_red = pca.transform(X_train)
# X_test_red = pca.transform(X_test)
X_train_red = apply_pca(X_train, n_components)
X_test_red = apply_pca(X_test, n_components)

accuracy = (naive_b(X_train_red, y_train, X_test_red, y_test, 500))
print(f"Accuracy of 500 dimension MNIST dataset using NB algo:-{(accuracy*100):.4f} %")
print(y_test)

