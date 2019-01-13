import os
import re
import pickle
from smswebservice.settings import STATIC_ROOT
from django.http import HttpResponse
from nltk.tokenize import word_tokenize
PICKLE_FOLDER = os.path.join(STATIC_ROOT, 'sms_classifier_pickle')

def classify_text(request):
    to_be_classified = request.GET.get('string')
    
    def convertAlay(text):
        words = word_tokenize(text)
        new_string = ''
        for msg in words:
            new_word = ''
            alpha_flag = False
            digit_flag = False
            for c in msg:
                if c.isalpha():
                    alpha_flag = True
                elif c.isdigit():
                    digit_flag = True
            
            if alpha_flag and digit_flag:
                msg = msg.lower()
                if msg[-4:] != 'ribu' and msg[-3:] != 'rbu' and msg[-2:] != 'rb':
                    for c in msg:
                        if c == '1':
                            c = 'i'
                        elif c == '2':
                            c = 's'
                        elif c == '3':
                            c = 'e'
                        elif c == '4':
                            c = 'a'
                        elif c == '5':
                            c = 's'
                        elif c == '6':
                            c = 'g'
                        elif c == '7':
                            c = 't'
                        elif c == '8':
                            c = 'b'
                        elif c == '9':
                            c = 'g'
                        elif c == '0':
                            c = 'o'
                        new_word = new_word + c
            
            if new_word != '':
                new_string = new_string + new_word + ' '
            else:
                new_string = new_string + msg + ' '

        return new_string

    def preproccess_text(text_messages):
        # Convert if text is "alay"
        processed = convertAlay(text_messages)

        # change words to lower case - Hello, HELLO, hello are all the same word
        processed = processed.lower()

        # Replace email addresses with 'almtemail'
        processed = re.sub(r'^.+@[^\.].*\.[a-z]{2,}$', ' almtemail ', processed)

        # Replace URLs with 'almtweb'
        processed = re.sub(r'[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', 'almtweb', processed)
        processed = processed.replace('http', '')
        processed = processed.replace('https', '')
        
        # Replace money symbols with 'symbuang' (£ can by typed with ALT key + 156)
        processed = re.sub(r'£|\$', 'symbuang ', processed)
        processed = processed.replace(' rp.', ' symbuang ')
        processed = processed.replace(' rp', ' symbuang ')
            
        # Replace 10 digit phone numbers (formats include paranthesis, spaces, no spaces, dashes) with 'phonenumber'
        processed = re.sub(r'^\(?[\d]{3}\)?[\s-]?[\d]{3}[\s-]?[\d]{4}$', 'nmrtlpn', processed)
            
        # Replace numbers with 'noomr'
        processed = re.sub(r'\d+(\.\d+)?', 'noomr', processed)

        # Remove punctuation
        processed = re.sub(r'[.,\/#!%\^&\*;:{}=\-_`~()?]', ' ', processed)
        processed = re.sub(r'\s[a-z]\s', '', processed)

        # Replace whitespace between terms with a single space
        processed = re.sub(r'\s+', ' ', processed)

        # Remove leading and trailing whitespace
        processed = re.sub(r'^\s+|\s+?$', '', processed)
        return processed

    #Open word features
    word_features_f = open(os.path.join(PICKLE_FOLDER , "word_features.pickle"), "rb")
    word_features = pickle.load(word_features_f)
    word_features_f.close()

    # The find_features function will determine which of the 1500 word features are contained in the review
    def find_features(message):
        words = word_tokenize(message)
        features = {}
        for word in word_features:
            features[word] = (word in words)

        return features

    # Define models to train
    names = ["SVM Linear"]

    normal_msg = 0
    promo_msg = 0
    spam_msg = 0

    for name in names:
        classifier_s = open(os.path.join(PICKLE_FOLDER , name + ' Classifier.pickle'), "rb")
        sms_classifier = pickle.load(classifier_s)
        classifier_s.close()
        
        result = sms_classifier.classify(find_features(preproccess_text(to_be_classified)))
        if result == 0:
            normal_msg = normal_msg + 1
        elif result == 1:
            promo_msg = promo_msg + 1
        elif result == 2:
            spam_msg = spam_msg + 1
        
    if normal_msg >= promo_msg and normal_msg >= spam_msg:
        best_result = "normal"
        confidence = normal_msg / (normal_msg + promo_msg + spam_msg)
    elif promo_msg >= normal_msg and promo_msg >= spam_msg:
        best_result = "promo"
        confidence = promo_msg / (normal_msg + promo_msg + spam_msg)
    elif spam_msg >= normal_msg and spam_msg >= promo_msg:
        best_result = "spam"
        confidence = spam_msg / (normal_msg + promo_msg + spam_msg)

    return HttpResponse(best_result)