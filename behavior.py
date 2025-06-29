## Adult stage midge's behavior neural network.
from os import access
import numpy as np

class NeuralNetwork:
    def __init__(self, inputs, outputs, layers = [12, 2, 4], learning_rate = 0.001, iterations = 500):

        self.learning_rate = learning_rate
        self.iteration = iterations
        self.layers = layers
        self.inputs = inputs #perceptions
        self.outputs = outputs #actions
        self.weights = np.random.randn(len(self.inputs), len(self.outputs))
        self.bias = 1.0

    def forward(self, inputs):
        return np.dot(self.weights, self.inputs) + self.bias

    def backward(self):
        #TODO
        pass

    def activation(self, input):
        #Sigmoid
        return 1 / (1 + np.exp(-input))
        

### TEST ###

nn = NeuralNetwork([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0], [1, 2, 3, 4])
print(nn.weights)

for i in range(len(nn.inputs)):
    print(nn.activation(i))
    

