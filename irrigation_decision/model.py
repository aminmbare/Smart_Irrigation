import pandas as pd 
from sklearn.model_selection import train_test_split
from tensorflow import keras  
from keras.models import  Sequential 
from keras.layers import Dense
from keras.utils import plot_model
import tensorflow as tf
dataset=pd.read_csv("irrigation_decision/data.csv")
x=dataset.iloc[:,1:3].values
y=dataset.iloc[:,3].values
#split the data 
x_train,x_test,y_train, y_test=train_test_split(x,y,test_size=0.1,random_state=0)


def model(hidden_layers, neurons):
    cl = Sequential()
    #input layer
    cl.add(Dense(neurons , input_dim = 2 , kernel_initializer = "random_uniform" , bias_initializer='zeros', activation="relu"))
    for _ in range(hidden_layers):
        # hidden layer 
        cl.add(Dense(6, kernel_initializer='random_uniform',
                bias_initializer='zeros', activation="relu"))
    cl.add(Dense(1 , kernel_initializer='random_uniform',
                bias_initializer='zeros', activation="sigmoid"))
    cl.compile(optimizer="adam",loss="binary_crossentropy",metrics=['accuracy'])
    return cl 

if __name__ == "__main__":
    ann = model(3,6)
    ann.fit(x_train, y_train, batch_size=5, epochs=20)
    print(ann.summary())
    plot_model(ann,'model.jpg',show_shapes=True)
    print(type(x_test))
    print(x_test[1].shape)
    _,accuracy=ann.evaluate(x_test, y_test)
    
    print(f'Accuracy: {accuracy*100}')
    ann.save('irrigation_decision.h5')
    print(f'prediction{ann.predict([[200,33]])}')

