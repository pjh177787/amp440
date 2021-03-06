import numpy as np
import math
import matplotlib.pyplot as plt

class Bayesian_Model_Face:
    def __init__(self):
        self.training_classes = 
            [
                [{'#':0, ' ':0} for i in range(60)]
                for i in range(70)]
        self.training_labels = []
        self.testing_classes =  [
            [
                [' ' for i in range(60)]
                for i in range(70)]
            for i in range(150)]
        self.testing_labels = []
        self.confusion_matrix = np.zeros((10, 10))
        self.count = np.zeros(10) # count of appearances of each number in the training sample
        self.priors = np.zeros(10)

    def parse_file(self, trainfile_name, trainlabel_name, testfile_name, testlabel_name,  smooth_factor):
        trainfile = open(trainfile_name, 'r')
        trainlabel = open(trainlabel_name, 'r')
        for line in trainlabel:
            for ch in line:
                if ch.isdigit():
                    self.training_labels.append(int(ch))
        for label in self.training_labels:
            self.count[label] += 1
            for i in range(70):
                image_line = trainfile.readline()
                for j in range(len(image_line)):
                    self.training_classes[label][i][j][image_line[j]] += 1
        trainfile.close()

        self.laplace_smooth(smooth_factor)
        self.prior()

        testfile = open(testfile_name, 'r')
        testlabel = open(testlabel_name, 'r')
        for line in testlabel:
            for ch in line:
                if ch.isdigit():
                    self.testing_labels.append(int(ch))      
        for idx in range(len(self.testing_labels)):
            for i in range(70):
                image_line = testfile.readline()
                print(len(image_line))
                for j in range(len(image_line)):
                    self.testing_classes[idx][i][j] = image_line[j]
        testfile.close()

    def laplace_smooth(self, factor):
        for num in range(10):
            if self.count[num] > 0:
                denom = math.log2(self.count[num] + factor*2)
            else:
                denom = float('-inf')
            for i in range(70):
                for j in range(len(image_line)):
                    for pixel in self.training_classes[num][i][j]:
                        self.training_classes[num][i][j][pixel] = math.log2(self.training_classes[num][i][j][pixel] + factor)  - denom

    def prior(self):
        total_count = sum(self.count)
        self.priors = [num/total_count for num in self.count]

    def test(self):
        self.parse_file('./facedata/facedatatrain', './facedata/facedatatrainlabels', './facedata/facedatatest', './facedata/facedatatestlabels', 1)

        predictions = []
        correct_counts = [0 for i in range(10)]
        total_counts = [0 for i in range(10)]
        correct = 0
        each = 0
        line = 0
        largest_posterior = [[float('-inf'), " "] for i in range(10)]
        smallest_posterior = [[float('inf'), " "] for i in range(10)]
        
        for label in self.testing_labels:
            maxi = float('-inf')
            mini = float('inf')
            predicted = 0
            for each_possibility in range(10):
                possibility = math.log2(self.priors[each_possibility])
                for i in range(70):
                    for j in range(32):
                        pixel = self.testing_classes[each][i][j]
                        possibility += self.training_classes[each_possibility][i][j][pixel]
                if possibility > maxi:
                    predicted = each_possibility
                    maxi = possibility
                if possibility < mini:
                    mini = possibility
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
        print(smallest_posterior)

        print('Classification Rate For Each Digit:')
        for i in range(10):
            print(i, correct_counts[i]/total_counts[i])

        print('Confusion Matrix:')
        for i in range(10):
            print(self.confusion_matrix[i])

        print(predictions)
        print(correct_prec)

        confusion_tuple = [((i, j), self.confusion_matrix[i][j]) for j in range(10) for i in range(10)]
        confusion_tuple = list(filter(lambda x: x[0][0] != x[0][1], confusion_tuple))
        confusion_tuple.sort(key = lambda x: -x[1])
        
        for i in range(4):
            feature1_pre = self.training_classes[confusion_tuple[i][0][0]]
            feature1 = [[chardict['1'] for chardict in row] for row in feature1_pre]
            feature2_pre = self.training_classes[confusion_tuple[i][0][1]]
            feature2 = [[chardict['1'] for chardict in row] for row in feature2_pre]

            fig = [None for k in range(3)]
            axes = [None for k in range(3)]
            heatmap = [None for k in range(3)]
            features =  [feature1,feature2, list(np.array(feature1) - np.array(feature2))]
            for k in range(3):
                fig[k], axes[k] = plt.subplots()  
                heatmap[k] = axes[k].pcolor(features[k], cmap="jet")
                axes[k].invert_yaxis()
                axes[k].xaxis.tick_top()
                plt.tight_layout()
                plt.colorbar(heatmap[k])
                plt.show()
                # plt.savefig('src/binaryheatmap%.0f%d.png' % (i + 1, k + 1) )
            
