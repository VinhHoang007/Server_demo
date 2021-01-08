import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle, os
import numpy as np
from tensorflow.keras.models import load_model
import json, dbconfig, statistics
import random
from flask import Flask
from flaskext.mysql import MySQL
import matplotlib.pyplot as plt


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower() )for word in sentence_words]
    return sentence_words


def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))


def predict_class(sentence, model, jsname):
    words = pickle.load(open('./words/'+jsname+'.pkl','rb'))
    classes = pickle.load(open('./classes/'+jsname+'.pkl','rb'))
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    # retest = [[i,r] for i,r in enumerate(res)]
    # retest.sort(key=lambda x: x[1], reverse=True)
    # x=[]
    # y=[]
    # for r in retest:
    #     y.append(classes[r[0]])
    #     x.append(r[1])
    # plt.plot(x,y,'go-')
    # plt.show()
    res_pvar = 0
    max_pvar = max(res)
    for r in res:
        res_pvar = res_pvar + (r-max_pvar)*(r-max_pvar)
    #print(res_pvar/len(res))
    return res_pvar/len(res), res, classes



def takeelelist(lists, num):
    results = []
    count = 0
    for i in lists:
        results.append(i)
        count = count + 1
        if count == num:
            break
    return results


def getResponse(ints,intents_json,jsname,course):
    app = Flask(__name__)
    if ints == None:
        return 'Hệ thống không tìm thấy dữ liệu phù hợp ! Bạn vui lòng thử lại nhé !'
    for i in ints:
        if (i['intent']=='HT' or i['intent']=='SH' or i['intent']=='TQ'):
            condition = i['intent']
            condition_val = float(i['probability'])
            ints.remove(i)
            for j in ints:
                if (j['intent']!='HT' and j['intent']!='SH' and j['intent']!='TQ'):
                    subjectid = j['intent']
                    subjectid_val = float(j['probability'])
                    if (subjectid_val<0.001 or condition_val<0.001):
                        return 'Hệ thống không tìm thấy dữ liệu phù hợp ! Bạn vui lòng thử lại nhé !'
                    elif subjectid == 'EE3151':
                        return '''Để làm đồ án bạn cần học trước các môn bắt buộc cơ sở ngành, không có 
                                môn song hành hay tiên quyết bạn nhé !'''
                    elif subjectid == 'EE3333':
                        return dbconfig.subconfig(subjectid,app,condition,course) + '''
                           Ngoài ra, để đăng ký môn này, bạn được nợ tối đa 16 tín chỉ tính theo số tín chỉ tích 
                           lũy ngành của khóa/ngành khi học đúng tiến độ. Khi tính số tín chỉ tích lũy ngành, các 
                           môn đã đăng ký học trong học kỳ chính kế trước được xem như đạt (không tính môn dự thính).'''
                    elif subjectid == 'EE4333':
                        return dbconfig.subconfig(subjectid,app,condition,course) + '''
                            Ngoài ra, để đăng ký môn này, bạn được nợ tối đa 7 tín chỉ tính theo số tín chỉ tích 
                            lũy ngành của khóa-ngành khi học đúng tiến độ. Khi tính số tín chỉ tích lũy ngành, 
                            các môn đã đăng ký học trong học kỳ chính kế trước được xem như đạt (không tính môn dự thính) 
                            và cần phải thỏa điều kiện anh văn, ngày công tác xã hội để đăng ký môn này.'''
                    else:
                        return dbconfig.subconfig(subjectid,app,condition,course) + 'bạn nhé !'
    for i in ints:
        if (i['intent']=='CAV1' or i['intent']=='CAV2' or i['intent']=='CAV3' or i['intent']=='CAVLV' or i['intent']=='CAVTN'):
            course = ''
            year = i['intent']
            ints.remove(i)
            for j in ints:
                if (j['intent'] == '2017' or j['intent'] == '2018' or j['intent'] == '2019'): 
                    course = j['intent']
                    return dbconfig.avstand(year,course,app)
        elif (i['intent']=='CSV1' or i['intent']=='CSV2' or i['intent']=='CSV3' or i['intent']=='CSV4' or i['intent']=='CSV5' ):
            course = "NULL"
            sv = i['intent']
            return dbconfig.avstand(sv,course,app)

    for i in ints:
        if (i['intent']=='INFO'):
            ints.remove(i)
            teacher = ints[0]['intent']
            app = Flask(__name__)
            return dbconfig.teachinfo(teacher,app)
    
    tag = ints[0]['intent']
    list_of_intents = intents_json[jsname]
    for i in list_of_intents:
        if(i['tag']==tag):
            result = random.choice(i['responses'])
            break
    if result=="":
        result = 'Hiện tại Bot chưa hiểu yêu cầu của bạn ! Bạn vui lòng thử lại nhé !'
    return result


def chatbot_response(msg, course):
    arr = os.listdir('./json file')
    max_pvar = -1
    for i in arr:
        jsname_pre = os.path.splitext(i)[0]
        model = load_model('./model h5/'+ jsname_pre +'.h5')
        pvar, res_pvar, classes_pvar =  predict_class(msg, model, jsname_pre)
        print(jsname_pre, pvar)
        if (max_pvar<=pvar):
            max_pvar = pvar
            res = res_pvar
            jsname = jsname_pre
            classes = classes_pvar
    if (max_pvar>0.3):
        retest = [[i,r] for i,r in enumerate(res)]
        retest.sort(key=lambda x: x[1], reverse=True)
        for r in retest:
            print("intent: "+classes[r[0]]+" "+str(r[1]))
        ints = []
        for r in retest:
            ints.append({"intent": classes[r[0]], "probability": str(r[1])})
        jsload = json.loads(open('./json file/'+jsname+'.json',encoding='utf8').read())
        result = getResponse(ints, jsload, jsname, course)
    else:
        result = getResponse(None,None,None, course)
    return result