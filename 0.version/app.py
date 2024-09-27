import streamlit as st
import pickle
import re
import nltk
import json

nltk.download('punkt')
nltk.download('stopwords')

# Loading models
clf = pickle.load(open('clf.pkl','rb'))
tfidfd = pickle.load(open('tfidf.pkl','rb'))

# Preprocessing
def cleanResume(txt):
    cleanText = re.sub('http\S+\s', ' ', txt) # http://web.com
    cleanText = re.sub('RT|cc', ' ', cleanText) # RT @user: This is an amazing tweet! cc @anotheruser
    cleanText = re.sub('#\S+\s', ' ', cleanText) # ## #### ###
    cleanText = re.sub('@\S+', '  ', cleanText) # @gmail.com
    cleanText = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', cleanText) # Punctuation
    cleanText = re.sub(r'[^\x00-\x7f]', ' ', cleanText) # Café, jalapeño, résumé
    cleanText = re.sub('\s+', ' ', cleanText) # This   is   a    test.
    return cleanText

with open('mapping.txt', 'r') as f:
    mapping = json.load(f)

# Web app
def main():
    st.title("Resume Screening App")
    uploaded_file = st.file_uploader('Upload Resume', type=['txt','pdf'])

    if uploaded_file is not None:
        try:
            resume_bytes = uploaded_file.read()
            resume_text = resume_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # If UTF-8 decoding fails, try decoding with 'latin-1'
            resume_text = resume_bytes.decode('latin-1')

        cleaned_resume = cleanResume(resume_text)
        input_features = tfidfd.transform([cleaned_resume])
        prediction_id = clf.predict(input_features)[0]
        st.write(prediction_id)

        category_name = mapping.get(f'{prediction_id}', "Unknown")
        st.write("Predicted Category:", category_name)
        
if __name__ == "__main__":
    main()
