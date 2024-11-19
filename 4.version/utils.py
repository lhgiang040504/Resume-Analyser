import os
import re
import io
import spacy
import docx2txt
import constants as cs

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFSyntaxError

import pandas as pd
from datetime import datetime
from dateutil import relativedelta
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

import nltk
from collections import defaultdict
from urllib.parse import urlparse


# Handle input file
def extract_text_from_pdf(pdf_path):
    '''
    Helper function to extract the plain text from .pdf files

    :param pdf_path: path to PDF file to be extracted (remote or local)
    :return: iterator of string of extracted text
    '''
    # https://www.blog.pythonlibrary.org/2018/05/03/exporting-data-from-pdfs-with-python/
    if not isinstance(pdf_path, io.BytesIO):
        # extract text from local pdf file
        with open(pdf_path, 'rb') as fh:
            try:
                for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
                    resource_manager = PDFResourceManager()
                    fake_file_handle = io.StringIO()

                    converter = TextConverter(resource_manager, fake_file_handle, codec='utf-8', laparams=LAParams())
                    page_interpreter = PDFPageInterpreter(resource_manager, converter)

                    page_interpreter.process_page(page)
                    text = fake_file_handle.getvalue()
                    # it can produce a sequence of text chunks
                    yield text

                    # close open handles
                    converter.close()
                    fake_file_handle.close()
            except PDFSyntaxError:
                return
    else:
        # extract text from remote pdf file
        try:
            for page in PDFPage.get_pages(pdf_path, caching=True, check_extractable=True):
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()

                converter = TextConverter(resource_manager, fake_file_handle, codec='utf-8', laparams=LAParams())
                page_interpreter = PDFPageInterpreter(resource_manager, converter)

                page_interpreter.process_page(page)
                text = fake_file_handle.getvalue()
                # it can produce a sequence of text chunks
                yield text

                # close open handles
                converter.close()
                fake_file_handle.close()
        except PDFSyntaxError:
            return


def extract_text_from_docx(doc_path):
    '''
    Helper function to extract plain text from .docx files

    :param doc_path: path to .docx file to be extracted
    :return: string of extracted text
    '''
    try:
        temp = docx2txt.process(doc_path)
        text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
        return ' '.join(text)
    except KeyError:
        return ' '


def extract_text(file_path):
    '''
    Wrapper function to detect the file extension and call text
    extraction function accordingly

    :param file_path: path of file of which text is to be extracted
    :param extension: extension of file `file_name`
    '''
    extension = file_path.split('.')[-1]
    text = ''
    if extension == 'pdf':
        for page in extract_text_from_pdf(file_path):
            text += ' ' + page
    elif extension == 'docx':
        text = extract_text_from_docx(file_path)
    return text


def get_number_of_pages(file_name):
    try:
        if isinstance(file_name, io.BytesIO):
            # for remote pdf file
            count = 0
            for page in PDFPage.get_pages(
                        file_name,
                        caching=True,
                        check_extractable=True
            ):
                count += 1
            return count
        else:
            # for local pdf file
            if file_name.endswith('.pdf'):
                count = 0
                with open(file_name, 'rb') as fh:
                    for page in PDFPage.get_pages(
                            fh,
                            caching=True,
                            check_extractable=True
                    ):
                        count += 1
                return count
            else:
                return None
    except PDFSyntaxError:
        return None


# Handle raw text data
def extract_entity_sections_grad(text):
    '''
    Helper function to extract all the raw text from sections of resume
    specifically for graduates and undergraduates

    :param text: Raw text of resume
    :return: dictionary of entities
    '''
    text_split = [i.strip() for i in text.split('\n')]
    entities = {}
    key = False
    for phrase in text_split:
        if len(phrase) == 1:
            p_key = phrase
        else:
            p_key = set(phrase.lower().split()) & set(cs.RESUME_SECTIONS_GRAD)
        try:
            p_key = list(p_key)[0]
        except IndexError:
            pass
        if p_key in cs.RESUME_SECTIONS_GRAD:
            entities[p_key] = []
            key = p_key
        elif key and phrase.strip():
            entities[key].append(phrase)
    return entities


def extract_entity_sections_grad_(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)

    entities = {}
    for ent in doc.ents:
        if ent.label_ not in entities.keys():
            entities[ent.label_] = [ent.text]
        else:
            entities[ent.label_].append(ent.text)
    return entities


def extract_entities_wih_custom_model(custom_nlp_text):
    '''
    Helper function to extract different entities with custom
    trained model using SpaCy's NER

    :param custom_nlp_text: object of `spacy.tokens.doc.Doc`
    :return: dictionary of entities
    '''
    entities = {}
    for ent in custom_nlp_text.ents:
        if ent.label_ not in entities.keys():
            entities[ent.label_] = [ent.text]
        else:
            entities[ent.label_].append(ent.text)
    for key in entities.keys():
        entities[key] = list(set(entities[key]))
    return entities
    

# Parsing data
def get_total_experience(experience_list):
    '''
    Wrapper function to extract total months of experience from a resume

    :param experience_list: list of experience text extracted
    :return: total months of experience
    '''
    exp_ = []
    for line in experience_list:
        experience = re.search(r'(?P<fmonth>\w+.\d+)\s*(\D|to)\s*(?P<smonth>\w+.\d+|present)', line, re.I)
        if experience:
            exp_.append(experience.groups())
    total_exp = sum(
        [get_number_of_months_from_dates(i[0], i[2]) for i in exp_]
    )
    total_experience_in_months = total_exp
    return total_experience_in_months


def extract_experience(resume_text):
    '''
    Helper function to extract experience from resume text

    :param resume_text: Plain resume text
    :return: list of experience
    '''
    wordnet_lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    # word tokenization
    word_tokens = nltk.word_tokenize(resume_text)

    # remove stop words and lemmatize
    filtered_sentence = [
            w for w in word_tokens if w not
            in stop_words and wordnet_lemmatizer.lemmatize(w)
            not in stop_words
        ]
    sent = nltk.pos_tag(filtered_sentence)

    # parse regex
    cp = nltk.RegexpParser('P: {<NNP>+}')
    cs = cp.parse(sent)

    # for i in cs.subtrees(filter=lambda x: x.label() == 'P'):
    #     print(i)

    test = []

    for vp in list(
        cs.subtrees(filter=lambda x: x.label() == 'P')
    ):
        test.append(" ".join([
            i[0] for i in vp.leaves()
            if len(vp.leaves()) >= 2])
        )

    # Search the word 'experience' in the chunk and
    # then print out the text after it
    x = [
        x[x.lower().index('experience') + 10:]
        for i, x in enumerate(test)
        if x and 'experience' in x.lower()
    ]
    return x


def get_number_of_months_from_dates(date1, date2):
    '''
    Helper function to extract total months of experience from a resume

    :param date1: Starting date
    :param date2: Ending date
    :return: months of experience from date1 to date2
    '''
    if date2.lower() == 'present':
        date2 = datetime.now().strftime('%b %Y')
    try:
        if len(date1.split()[0]) > 3:
            date1 = date1.split()
            date1 = date1[0][:3] + ' ' + date1[1]
        if len(date2.split()[0]) > 3:
            date2 = date2.split()
            date2 = date2[0][:3] + ' ' + date2[1]
    except IndexError:
        return 0
    try:
        date1 = datetime.strptime(str(date1), '%b %Y')
        date2 = datetime.strptime(str(date2), '%b %Y')
        months_of_experience = relativedelta.relativedelta(date2, date1)
        months_of_experience = (months_of_experience.years
                                * 12 + months_of_experience.months)
    except ValueError:
        return 0
    return months_of_experience


def extract_entity_sections_professional(text):
    '''
    Helper function to extract all the raw text from sections of
    resume specifically for professionals

    :param text: Raw text of resume
    :return: dictionary of entities
    '''
    text_split = [i.strip() for i in text.split('\n')]
    entities = {}
    key = False
    for phrase in text_split:
        if len(phrase) == 1:
            p_key = phrase
        else:
            p_key = set(phrase.lower().split()) & set(cs.RESUME_SECTIONS_PROFESSIONAL)
        try:
            p_key = list(p_key)[0]
        except IndexError:
            pass
        if p_key in cs.RESUME_SECTIONS_PROFESSIONAL:
            entities[p_key] = []
            key = p_key
        elif key and phrase.strip():
            entities[key].append(phrase)
    return entities


def extract_link(text):
    '''
    Helper function to extract link id from text

    :param text: plain text extracted from resume file
    '''
    # Regular expression to match domain names with optional protocols and paths
    domain_with_path_pattern = cs.LINK_PATTERN
    # Extract all the links (with or without protocol)
    links = re.findall(domain_with_path_pattern, text)

    # Dictionary to hold domain as key and list of links as value
    domain_dict = defaultdict(list)

    # Iterate through each link
    for link in links:
        # If the link doesn't have a protocol, add https:// by default
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', link):  # No protocol
            link = 'https://' + link

        # Parse the link to get the domain name (without protocol)
        parsed_url = urlparse(link)
        domain_name = parsed_url.netloc

        # Append the link to the list of the corresponding domain
        domain_dict[domain_name].append(link)

    return domain_dict


def extract_name(doc, matcher):
    '''
    Helper function to extract name from spacy nlp text

    :param nlp_text: object of `spacy.tokens.doc.Doc`
    :param matcher: object of `spacy.matcher.Matcher`
    :return: string of full name
    '''
    # Add a pattern to match proper nouns (PROPN)
    pattern = cs.NAME_PATTERN
    matcher.add('NAME', None, pattern)

    # Apply the matcher to the doc
    matches = matcher(doc)
    
    # List to store full names
    full_names = []
    
    # Temporary variable to track the end position of the last matched name
    last_end_index = -1
    
    # Iterate over the matches
    for match_id, start, end in matches:
        # If the current match is contiguous with the last match, append the name
        if start == last_end_index:
            full_names[-1] += " " + doc[start:end].text  # Merge the names
        else:
            full_names.append(doc[start:end].text)  # Add a new name
        
        # Update the last_end_index to the end of the current match
        last_end_index = end
    
    return full_names

def extract_link(text):
    '''
    Helper function to extract link id from text

    :param text: plain text extracted from resume file
    '''
    # Regular expression to match domain names with optional protocols and paths
    domain_with_path_pattern = cs.LINK_PATTERN
    # Extract all the links (with or without protocol)
    links = re.findall(domain_with_path_pattern, text)

    # Dictionary to hold domain as key and list of links as value
    domain_dict = defaultdict(list)

    # Iterate through each link
    for link in links:
        # If the link doesn't have a protocol, add https:// by default
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', link):  # No protocol
            link = 'https://' + link

        # Parse the link to get the domain name (without protocol)
        parsed_url = urlparse(link)
        domain_name = parsed_url.netloc

        # Append the link to the list of the corresponding domain
        domain_dict[domain_name].append(link)

    return domain_dict

def extract_mobile_number(text):
    '''
    Helper function to extract mobile number from text.

    :param text: plain text extracted from a resume file
    :return: list of extracted mobile numbers
    '''
    # Enhanced regex to match international formats and balanced parentheses
    mob_num_regex = r'''(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)
                        [-\.\s]*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'''
    phone = re.findall(re.compile(mob_num_regex), text)

    return phone

def extract_education(nlp_text):
    '''
    Helper function to extract education from spacy nlp text

    :param nlp_text: object of `spacy.tokens.doc.Doc`
    :return: tuple of education degree and year if year if found
             else only returns education degree
    '''
    edu = {}
    # Extract education degree
    try:
        for index, token in enumerate(nlp_text):
            text_cleaned = re.sub(r'[?|$|.|!|,]', r'', token.text)
            if text_cleaned.upper() in cs.EDUCATION and text_cleaned.upper() not in cs.STOPWORDS:
                # Collect surrounding context (current and next 5 tokens for simplicity)
                context = " ".join([t.text for t in nlp_text[index:index + 6]])
                edu[text_cleaned.upper()] = context
    except IndexError:
        pass

    # Extract year
    education = []
    for key in edu.keys():
        year = re.search(re.compile(cs.YEAR), edu[key])
        if year:
            education.append((key, ''.join(year.group(0))))
        else:
            education.append(key)
    return education

def extract_skills(nlp_text, noun_chunks, skills_file=None):
    '''
    Helper function to extract skills from spacy nlp text

    :param nlp_text: object of `spacy.tokens.doc.Doc`
    :param noun_chunks: noun chunks extracted from nlp text
    :return: list of skills extracted
    '''
    tokens = [token.text for token in nlp_text if not token.is_stop]
    if not skills_file:
        data = pd.read_csv(
            os.path.join(os.path.dirname(__file__), 'skills.csv')
        )
    else:
        data = pd.read_csv(skills_file)
    skills = list(data.columns.values)
    skillset = []
    # check for one-grams
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)

    # check for bi-grams and tri-grams
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    return [i.capitalize() for i in set([i.lower() for i in skillset])]

def cleanup(token, lower=True):
    if lower:
        token = token.lower()
    return token.strip()