# Author: Omkar Pathak
import os
import multiprocessing as mp
import io
import spacy
import pprint
from spacy.matcher import Matcher
import utils


class ResumeParser(object):
    def __init__(self, resume, skills_file=None):
        nlp = spacy.load('en_core_web_sm')
        custom_nlp = spacy.load(os.path.join(os.getcwd(), 'trainning', 'model'))
        self.__matcher = Matcher(nlp.vocab)
        self.__details = {
            'name': None,
            'links': None,
            'mobile_number': None,
            'skills': None,
            'college_name': None,
            'degree': None,
            'designation': None,
            'experience': None,
            'company_names': None,
            'no_of_pages': None,
            'total_experience': None,
        }
        
        # Skills file
        self.__skills_file = skills_file
        
        # Resume path
        self.__resume = resume

        # Extract text
        self.__text_raw = utils.extract_text(self.__resume)
        self.__text = ' '.join(self.__text_raw.split())
        
        # Load model
        self.__nlp = nlp(self.__text)
        self.__custom_nlp = custom_nlp(self.__text_raw)
        
        # Noun phrases
        self.__noun_chunks = list(self.__nlp.noun_chunks)
        
        self.__get_basic_details()

    def get_extracted_data(self):
        return self.__details

    def __get_basic_details(self):
        cust_ent = utils.extract_entities_wih_custom_model(self.__custom_nlp)
        
        full_names = utils.extract_name(self.__nlp, matcher=self.__matcher)
        links = utils.extract_link(self.__text)
        mobile = utils.extract_mobile_number(self.__text)
        skills = utils.extract_skills(self.__nlp, self.__noun_chunks, self.__skills_file)
        edu = utils.extract_education([sent.string.strip() for sent in self.__nlp.sents])
        entities = utils.extract_entity_sections_grad(self.__text_raw)

        # extract name
        try:
            self.__details['name'] = cust_ent['Name'][0]
        except (IndexError, KeyError):
            self.__details['name'] = full_names
        
        # extract email
        self.__details['links'] = links
        # extract mobile number
        self.__details['mobile_number'] = mobile
        # extract skills
        self.__details['skills'] = skills
        
        # extract college name
        try:
            self.__details['college_name'] = entities['College Name']
        except KeyError:
            pass
        # extract education Degree
        try:
            self.__details['degree'] = cust_ent['Degree']
        except KeyError:
            pass
        # extract designation
        try:
            self.__details['designation'] = cust_ent['Designation']
        except KeyError:
            pass
        # extract company names
        try:
            self.__details['company_names'] = cust_ent['Companies worked at']
        except KeyError:
            pass
        # extract experience
        try:
            self.__details['experience'] = entities['experience']
            try:
                exp = round(utils.get_total_experience(entities['experience']) / 12, 2)
                self.__details['total_experience'] = exp
            except KeyError:
                self.__details['total_experience'] = 0
        except KeyError:
            self.__details['total_experience'] = 0
        self.__details['no_of_pages'] = utils.get_number_of_pages(self.__resume)
        
        return

def resume_result_wrapper(resume):
    parser = ResumeParser(resume)
    return parser.get_extracted_data()
