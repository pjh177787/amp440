from random import seed, randrange
from copy import deepcopy
import numpy as np

class Preceptron:
    def __init__(self, trainfile_name, testfile_name):
        self.training_classes = []
        self.training_labels = []
        self.testing_classes =  []
        self.testing_labels = []
        self.weight_list = np.zeros((10, 1025))
        self.confusion_matrix = np.zeros((10, 10))

        self.parse_files(trainfile_name, testfile_name)

    def parse_files(self, trainfile_name, testfile_name):
        trainfile = open(trainfile_name, 'r')
        for line in trainfile:
            if len(line) < 32:
                for ch in line:
                    if ch.isdigit():
                        self.training_labels.append(int(ch))
        trainfile.seek(0)
        for label in self.training_labels:
            image = []
            for i in range(32):
                image_line = trainfile.readline()
                for j in range(32):
                    image.append(int(image_line[j]))
            image_line = trainfile.readline()
            for ch in image_line:
                if ch.isdigit() and int(ch) != label:
                    print('TRAINFILE ALIGN ERROR')
            self.training_classes.append(image)
        trainfile.close()

        testfile = open(testfile_name, 'r')
        for line in testfile:
            if len(line) < 32:
                for ch in line:
                    if ch.isdigit():
                        self.testing_labels.append(int(ch))
        testfile.seek(0) 
        for label in self.testing_labels:
            image = []
            for i in range(32):
                image_line = testfile.readline()
                for j in range(32):
                    image.append(int(image_line[j]))
            image_line = testfile.readline()
            for ch in image_line:
                if ch.isdigit() and int(ch) != label:
                    print('TESTFILE ALIGN ERROR')
            self.testing_classes.append(image)
        testfile.close()

    # Make a prediction with weights
    def predict(self, row, weights):
        activation = weights[-1]
        for i in range(len(row) - 1):
            activation += weights[i] * row[i]
        if activation >= 0:
            return 1, activation
        else:
            return 0, activation

    def train_weights(self, training_data, target_labels, learning_rate, num_epoch):
        learning_curve = np.zeros((10, num_epoch))
        for label in range(10):
            data_set = []
            for idx in range(len(training_data)):
                if label == target_labels[idx]:
                    row = training_data[idx] + [1]
                else:
                    row = training_data[idx] + [0]
                data_set.append(row)
            learning_rate_new = learning_rate
            for epoch in range(num_epoch):
                total_error = 0
                for row in data_set:
                    prediction = self.predict(row, self.weight_list[label])[0]
                    error = row[-1] - prediction
                    total_error += error**2
                    self.weight_list[label][-1] = self.weight_list[label][-1] + learning_rate_new*error
                    for i in range(len(row) - 1):
                        self.weight_list[label][i] = self.weight_list[label][i] + learning_rate_new*error*row[i]
                # print('Digit#%d, epoch #%d, learning_rate = %.3f, error = %.3f' %(label, epoch, learning_rate_new, total_error))
                learning_curve[label][epoch] = total_error
                learning_rate_new *= 0.9
                # if total_error < learning_rate:
                    # break
        return learning_curve

    def perceptron_train(self, learning_rate = 0.05, num_epoch = 10):
        return self.train_weights(self.training_classes, self.training_labels, learning_rate, num_epoch)

    def perceptron_test(self, bias_en = True):
        predictions = []
        correct_counts = [0 for i in range(10)]
        total_counts = [0 for i in range(10)]
        correct = 0
        each = 0
        line = 0
        largest_posterior = [[float('-inf'), " "] for i in range(10)]
        smallest_posterior = [[float('inf'), " "] for i in range(10)]

        if bias_en:
            bias = [1]
        else:
            bias = [0]
        for idx in range(len(self.testing_labels)):
            maxi = float('-inf')
            mini = float('inf')
            predicted = 0
            label = self.testing_labels[idx]
            candidates = []
            for each_possibility in range(10):
                row = self.testing_classes[idx] + bias
                actuation, possibility = self.predict(row, self.weight_list[each_possibility])
                if possibility > maxi:
                    predicted = each_possibility
                    maxi = possibility
                if possibility < mini:
                    mini = possibility
                if actuation == 1:
                    candidates.append((each_possibility, possibility))
            # print(candidates)
            
            predictions.append(predicted)
            if maxi > largest_posterior[label][0]:
                largest_posterior[label][0] = maxi
                largest_posterior[label][1] = line
            if mini < smallest_posterior[label][0]:
                smallest_posterior[label][0] = mini
                smallest_posterior[label][1] = line

            self.confusion_matrix[predicted][label] += 1

            if label == predicted:
                correct += 1
                correct_counts[label] += 1
            total_counts[label] += 1

            each += 1
            line += 33

        correct_prec = correct / each
        for i in range(10):
            for j in range(10):
                num = self.confusion_matrix[i][j]
                self.confusion_matrix[i][j] = num/total_counts[j]

        print('For each digit, show the test examples from that class that have the highest and lowest posterior probabilities according to your classifier.')
        print(largest_posterior)
        print('\n')
        print(smallest_posterior)

        print('Classification Rate For Each Digit:')
        for i in range(10):
            print(i, correct_counts[i]/total_counts[i])

        print('Confusion Matrix:')
        for i in range(10):
            print(self.confusion_matrix[i])

        print(predictions)
        print(correct_prec)

        # confusion_tuple = [((i, j), self.confusion_matrix[i][j]) for j in range(10) for i in range(10)]
        # confusion_tuple = list(filter(lambda x: x[0][0] != x[0][1], confusion_tuple))
        # confusion_tuple.sort(key = lambda x: -x[1])
        
        # for i in range(4):
        #     feature1_pre = self.training_classes[confusion_tuple[i][0][0]]
        #     feature1 = [[chardict['1'] for chardict in row] for row in feature1_pre]
        #     feature2_pre = self.training_classes[confusion_tuple[i][0][1]]
        #     feature2 = [[chardict['1'] for chardict in row] for row in feature2_pre]

        #     fig = [None for k in range(3)]
        #     axes = [None for k in range(3)]
        #     heatmap = [None for k in range(3)]
        #     features =  [feature1,feature2, list(np.array(feature1) - np.array(feature2))]
        #     for k in range(3):
        #         fig[k], axes[k] = plt.subplots()  
        #         heatmap[k] = axes[k].pcolor(features[k], cmap="jet")
        #         axes[k].invert_yaxis()
        #         axes[k].xaxis.tick_top()
        #         plt.tight_layout()
        #         plt.colorbar(heatmap[k])
        #         # plt.show()
        #         plt.savefig('src/binaryheatmap%.0f%d.png' % (i + 1, k + 1) )
