import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import json
import pickle
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, LSTM
from keras.optimizers import SGD
import random
import os,shutil

def train(jsonname):
    shutil.copyfile('./words.pkl','./words/'+jsonname+'.pkl')
    shutil.copyfile('./classes.pkl','./classes/'+jsonname+'.pkl')
    words=[]
    classes = []
    documents = []
    ignore_words = ['?', '!','.']
    data_file = open('./json file/' + jsonname + '.json',encoding='utf8').read()
    intents = json.loads(data_file)
    for intent in intents[jsonname]:
        for pattern in intent['patterns']:
            #tokenize each word
            w = nltk.word_tokenize(pattern)
            words.extend(w)
            #add documents in the corpus
            documents.append((w, intent['tag']))
            # add to our classes list
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    # lemmaztize and lower each word and remove duplicates
    words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
    words = sorted(list(set(words)))
    classes = sorted(list(set(classes)))
    print (len(documents), "documents")
    print (len(classes), "classes", classes)
    print (len(words), "unique lemmatized words", words)

    pickle.dump(words,open('./words/' + jsonname + '.pkl','wb'))
    pickle.dump(classes,open('./classes/' + jsonname + '.pkl','wb'))

    
    training = []
    output_empty = [0] * len(classes)
    for doc in documents:
        bag = []
        pattern_words = doc[0]
        pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
        for w in words:
            bag.append(1) if w in pattern_words else bag.append(0)
        

        output_row = list(output_empty)
        output_row[classes.index(doc[1])] = 1

        training.append([bag, output_row])

    random.shuffle(training)
    training = np.array(training)
    train_x = list(training[:,0])
    train_y = list(training[:,1])




    model = Sequential()
    model.add(Dense(256, input_shape=(len(train_x[0]),), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(len(train_y[0]), activation='softmax'))
    sgd = SGD(lr=0.01, decay=1e-8, momentum=0.82, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
    #fitting and saving the model 
    hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=2)
    model.save('./model h5/' + jsonname + '.h5', hist)
    print("model created")


arr = os.listdir('./json file')
if os.path.exists('./model h5'):
    shutil.rmtree('./model h5')
if os.path.exists('./classes'):
    shutil.rmtree('./classes')
if os.path.exists('./words'):
    shutil.rmtree('./words')

os.mkdir('./words')
os.mkdir('./classes')
os.mkdir('./model h5')
for i in arr:
    train(os.path.splitext(i)[0])


