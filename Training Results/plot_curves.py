import sys
import numpy as np 
import matplotlib.pyplot as plt

def plot_curves(filename, num_epochs):
    train_losses = np.zeros((num_epochs))
    train_accs = np.zeros((num_epochs))
    val_losses = np.zeros((num_epochs))
    val_accs = np.zeros((num_epochs))

    with open(filename) as f:
        f.readline()
        for i in range(num_epochs):
            f.readline()
            f.readline()
            train_ln = f.readline()
            train_losses[i] = float(train_ln[12:18])
            train_accs[i] = float(train_ln[24:30])
            val_ln = f.readline()
            val_losses[i] = float(val_ln[10:16])
            val_accs[i] = float(val_ln[22:28])
            f.readline()
    
    x = np.arange(0, num_epochs, 1)

    # Plot losses
    plt.plot(x, train_losses, label="training")
    plt.plot(x, val_losses, label="validation")
    plt.title("Training vs. Validation Loss")
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()

    # Plot accuracies
    plt.plot(x, train_accs, label="training")
    plt.plot(x, val_accs, label="validation")
    plt.ylim(0.0, 1.0)
    plt.title("Training vs. Validation Accuracy")
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    exp_name = sys.argv[1]
    num_epochs = int(sys.argv[2])
    plot_curves(f"{exp_name}/{exp_name}.out", num_epochs)
