import os
import time
import sys

import pymupdf
from pdfRead import ReadPDF
import config
from USPAP import USPAP
from GPTquery import GPTQuery
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util

# model_name = "bert-base-uncased"
model = SentenceTransformer('all-MiniLM-L6-v2')


def cal_similarity(my_gpt: GPTQuery, text1, text2):
    if text1 == "" or text2 == "":
        return False

    embedding1 = my_gpt.get_similarity(text1)
    embedding2 = my_gpt.get_similarity(text2)

    # embeddings1 = model.encode(text1, convert_to_tensor=True)
    # embeddings2 = model.encode(text2, convert_to_tensor=True)
    # cosine_similarity = util.cos_sim(embeddings1, embeddings2)
    # return cosine_similarity.item()

    # cosine_sim = text_similarity(text1, text2)
    cosine_sim = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    return cosine_sim


# def traverse_titles(pdf: ReadPDF, my_gpt, uspap: USPAP, key: str, prompt_: str):
#     # similarities = dict()
#     # for title in pdf.content.keys():
#     #     if title == "":
#     #         continue
#     #     similarities[title] = cal_similarity(my_gpt, key, title.lower())
#     #     time.sleep(0.3)
#     # similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
#     # first = similarities[0]
#     # print(similarities)
#     # print()
#     content = pdf.content[first[0]].content_text
#     prompt = "{}\n\n{}".format(content, prompt_)
#     response = my_gpt.query(prompt)
#     if response == "Not Found":
#         return
#     uspap.fields["client"] = response


def get_answer(pdf: ReadPDF, my_gpt, uspap: USPAP, title: str, field: str, prompt_: str):
    content = pdf.content[title].content_text
    prompt = "{}\n\n{}".format(content, prompt_)
    response = my_gpt.query(prompt)
    if "Not Found" in response:
        return
    uspap.fields[field] = response


def check_required_fields(uspap: USPAP):
    missed_fields = list()
    for (key, value) in uspap.fields.items():
        if value is None:
            missed_fields.append(key)

    for key in missed_fields:
        print(key)


def check_inconsistencies(uspap: USPAP, my_gpt: GPTQuery, path: str):
    inconsistencies_fields = dict()
    my_gpt.upload_pdf(path)
    for (key, value) in uspap.fields.items():
        if value is None:
            continue
        if key == "client":
            prompt = ("Is " + uspap.fields[key].replace("\n", "")
                      + " the client? If the answer is Yes, only tell me Yes. Otherwise, tell me the reason.")
            response = my_gpt.get_answer_with_upload(prompt)
            if "Yes" not in response:
                inconsistencies_fields[key] = response
        elif key == "intended user(s)":
            prompt = ("Is(are) " + uspap.fields[key].replace("\n", "")
                      + "intended user(s)? If the answer is Yes, only tell me Yes. Otherwise, tell me the reason.")
            response = my_gpt.get_answer_with_upload(prompt)
            if "Yes" not in response:
                inconsistencies_fields[key] = response
        elif key == "the intended use":
            prompt = (uspap.fields[key].replace("\n", "")
                      + "Is the intended use correct? If the answer is Yes, only tell me Yes. Otherwise, tell me the reason.")
            response = my_gpt.get_answer_with_upload(prompt)
            if "Yes" not in response:
                inconsistencies_fields[key] = response
        elif key == "interest appraised":
            prompt = (uspap.fields[key].replace("\n", "") +
                      "Is the interest correct? If the answer is Yes, only tell me Yes. Otherwise, tell me the reason.")
            response = my_gpt.get_answer_with_upload(prompt)
            if "Yes" not in response:
                inconsistencies_fields[key] = response
        elif key == "type and definition of value":
            prompt = (uspap.fields[key].replace("\n", "") +
                      "Is the type and definition of value correct? "
                      "If the answer is Yes, only tell me Yes. Otherwise, tell me the reason.")
            response = my_gpt.get_answer_with_upload(prompt)
            if "Yes" not in response:
                inconsistencies_fields[key] = response
        elif key == "methods and techniques":
            prompt = (uspap.fields[key].replace("\n", "") +
                      "Are the methods and techniques correct? "
                      "If the answer is Yes, only tell me Yes. Otherwise, tell me the reason.")
            response = my_gpt.get_answer_with_upload(prompt)
            if "Yes" not in response:
                inconsistencies_fields[key] = response
        elif key == "value opinion(s) and conclusion(s)":
            prompt = (uspap.fields[key].replace("\n", "") +
                      "Are the value opinion(s) and conclusion(s) correct? "
                      "If the answer is Yes, only tell me Yes. Otherwise, tell me the reason.")
            response = my_gpt.get_answer_with_upload(prompt)
            if "Yes" not in response:
                inconsistencies_fields[key] = response
        elif key == "the scope of work used to develop the appraisal":
            prompt = (uspap.fields[key].replace("\n", "") +
                      "Is the scope of work used to develop the appraisal correct? "
                      "If the answer is Yes, only tell me Yes. Otherwise, tell me the reason.")
            response = my_gpt.get_answer_with_upload(prompt)
            if "Yes" not in response:
                inconsistencies_fields[key] = response
        elif key == "the reasons for excluding the sales comparison, cost, or income approach(es)":
            prompt = (uspap.fields[key].replace("\n", "") +
                      "Is the reasons for excluding the sales comparison, cost, or income approach(es) correct? "
                      "If the answer is Yes, only tell me Yes. Otherwise, tell me the reason.")
            response = my_gpt.get_answer_with_upload(prompt)
            if "Yes" not in response:
                inconsistencies_fields[key] = response
        elif key == "the subject sales and other transfers, agreements of sale, options, and listings":
            prompt = (uspap.fields[key].replace("\n", "") +
                      "Is the subject sales and other transfers, agreements of sale, options, and listings correct? "
                      "If the answer is Yes, only tell me Yes. Otherwise, tell me the reason.")
            response = my_gpt.get_answer_with_upload(prompt)
            if "Yes" not in response:
                inconsistencies_fields[key] = response
    for (key, value) in inconsistencies_fields.items():
        print(key + ":")
        print(value)


def fill_empty(uspap: USPAP, pdf_path: str, my_gpt: GPTQuery):
    my_gpt.upload_pdf(pdf_path)
    for (key, value) in uspap.fields.items():
        if value is not None:
            continue
        if key == "client":
            prompt = "Who is the client? If you can not find the answer, only tell me Not Found."
            response = my_gpt.get_answer_with_upload(prompt)
            if "Not Found" not in response:
                uspap.fields[key] = response
        elif key == "intended user(s)":
            prompt = "Who are the intended user(s)? If you can not find the answer, only tell me Not Found."
            response = my_gpt.get_answer_with_upload(prompt)
            if "Not Found" not in response:
                uspap.fields[key] = response
        elif key == "the intended use":
            prompt = "What is the intended use? If you can not find the answer, only tell me Not Found."
            response = my_gpt.get_answer_with_upload(prompt)
            if "Not Found" not in response:
                uspap.fields[key] = response
        elif key == "interest appraised":
            prompt = "What is the interest? If you can not find the answer, only tell me Not Found."
            response = my_gpt.get_answer_with_upload(prompt)
            if "Not Found" not in response:
                uspap.fields[key] = response
        elif key == "type and definition of value":
            prompt = "What is the type and definition of value? If you can not find the answer, only tell me Not Found."
            response = my_gpt.get_answer_with_upload(prompt)
            if "Not Found" not in response:
                uspap.fields[key] = response
        elif key == "the date of the report":
            prompt = "What is the date of the report? If you can not find the answer, only tell me Not Found."
            response = my_gpt.get_answer_with_upload(prompt)
            if "Not Found" not in response:
                uspap.fields[key] = response
        elif key == "the extent of any significant appraisal assistance":
            prompt = "What is the extent of appraisal assistance? If you can not find the answer, only tell me Not Found."
            response = my_gpt.get_answer_with_upload(prompt)
            if "Not Found" not in response:
                uspap.fields[key] = response
        elif key == "methods and techniques":
            prompt = "What are methods and techniques? If you can not find the answer, only tell me Not Found."
            response = my_gpt.get_answer_with_upload(prompt)
            if "Not Found" not in response:
                uspap.fields[key] = response
        elif key == "signed certification":
            prompt = "Is the certification signed? If the answer is Yes, only tell me Yes. Otherwise, tell me Not Found."
            response = my_gpt.get_answer_with_upload(prompt)
            if "Yes" in response:
                uspap.fields[key] = True
            else:
                uspap.fields[key] = False


    pass


def main():
    pdf_path = None
    pdf_format = 1
    if sys.argv[1] == "-i":
        pdf_path = sys.argv[2]
    else:
        print("wrong parameters, python main.py -i /path/to/file -f 1")
        exit()
    if sys.argv[3] == "-f":
        pdf_format = int(sys.argv[4])
    else:
        print("wrong parameters, python main.py -i /path/to/file -f 1")
        exit()

    my_gpt = GPTQuery()
    uspap = USPAP()
    pdf = ReadPDF(pdf_path, pdf_format)
    pdf.read_pdf()

    titles_str = str()
    titles_list = list()
    for i in range(0, len(pdf.content.keys())):
        title = list(pdf.content.keys())[i]
        if title == "":
            continue
        text = "text{}: {}\n".format(i, title)
        titles_list.append(title)
        titles_str = titles_str + f"{text}"
    titles_str = titles_str + "\n"

    for key in uspap.fields.keys():
        if key == "client":
            prompt1 = titles_str + (
                "Based on the information above, which text is the most similar to the string 'client'? "
                "Only tell me the number of text.")
            index = my_gpt.query(prompt1)
            title = titles_list[int(index)]

            prompt2 = ("Based on the information above, who is the client? "
                       "If you find it, only tell me the name. Otherwise, tell me Not Found.")
            get_answer(pdf, my_gpt, uspap, title, key, prompt2)
        elif key == "intended user(s)":
            prompt1 = titles_str + (
                "Based on the information above, which text is the most similar to the string 'intended user(s)'? "
                "Only tell me the number of text.")
            index = my_gpt.query(prompt1)
            title = titles_list[int(index)]

            prompt2 = ("Based on the information above, who are intended users? "
                       "If you find it, only tell me the answer. Otherwise, tell me Not Found.")
            get_answer(pdf, my_gpt, uspap, title, key, prompt2)
        elif key == "the intended use":
            prompt1 = titles_str + (
                "Based on the information above, which text is the most similar to the string 'the intended use'? "
                "Only tell me the number of text.")
            index = my_gpt.query(prompt1)
            title = titles_list[int(index)]

            prompt2 = "Based on the information above, what is the purpose of the appraisal?"
            get_answer(pdf, my_gpt, uspap, title, key, prompt2)
        elif key == "interest appraised":
            prompt1 = titles_str + (
                "Based on the information above, which text is the most similar to the string 'interest appraised'? "
                "Only tell me the number of text.")
            index = my_gpt.query(prompt1)
            title = titles_list[int(index)]

            prompt2 = "Based on the information above, what is the interest?"
            get_answer(pdf, my_gpt, uspap, title, key, prompt2)
        elif key == "type and definition of value":
            prompt1 = titles_str + (
                "Based on the information above, "
                "which text is the most similar to the string 'type and definition of value'? "
                "Only tell me the number of text.")
            index = my_gpt.query(prompt1)
            title = titles_list[int(index)]

            prompt2 = "Based on the information above, what is the definition of value?"
            get_answer(pdf, my_gpt, uspap, title, key, prompt2)
        elif key == "methods and techniques":
            prompt1 = titles_str + (
                "Based on the information above, "
                "which text is the most similar to the string 'methods and techniques'? "
                "Only tell me the number of text.")
            index = my_gpt.query(prompt1)
            title = titles_list[int(index)]

            prompt2 = "Based on the information above, what are the methods and techniques?"
            get_answer(pdf, my_gpt, uspap, title, key, prompt2)
        elif key == "value opinion(s) and conclusion(s)":
            pages = pdf.get_page("certification")  # letter
            pages = [1, pages[0]]
            path = "temp.pdf"
            new_pdf = pymupdf.open()
            new_pdf.insert_pdf(pdf.pdf, from_page=pages[0], to_page=pages[1])
            new_pdf.save(path)
            new_pdf.close()

            my_gpt.upload_pdf(path)
            prompt1 = "What is the date of the report?"
            response1 = my_gpt.get_answer_with_upload(prompt1)
            uspap.fields["the date of the report"] = response1

            prompt2 = "What is the value opinion(s) and conclusion(s)?"
            response2 = my_gpt.get_answer_with_upload(prompt2)
            uspap.fields["value opinion(s) and conclusion(s)"] = response2

            os.remove(path)
        elif key == "signed certification":
            pages = pdf.get_page("certification")
            if pages[0] == 0 and pages[1] == 0:
                continue
            path = "temp.pdf"
            new_pdf = pymupdf.open()
            new_pdf.insert_pdf(pdf.pdf, from_page=pages[0], to_page=pages[1])
            new_pdf.save(path)
            new_pdf.close()

            my_gpt.upload_pdf(path)
            prompt1 = "Is the certification signed? Please only tell me Yes or No."
            response1 = my_gpt.get_answer_with_upload(prompt1)
            if "Yes" in response1:
                uspap.fields["signed certification"] = True
            elif "No" in response1:
                uspap.fields["signed certification"] = False

            prompt2 = "What is the extent of any significant appraisal assistance?"
            response2 = my_gpt.get_answer_with_upload(prompt2)
            uspap.fields["the extent of any significant appraisal assistance"] = response2
            os.remove(path)
        elif key == "the scope of work used to develop the appraisal":

            my_gpt.upload_pdf(pdf_path)
            prompt1 = "What is the scope of work used to develop the appraisal? If you can not find, tell me Not Found."
            key1 = key
            response1 = my_gpt.get_answer_with_upload(prompt1)
            if "Not Found" not in response1:
                uspap.fields[key1] = response1

            prompt2 = "What is the reasons for excluding the sales comparison, cost, or income approach(es)? If you can not find, tell me Not Found."
            key2 = "the reasons for excluding the sales comparison, cost, or income approach(es)"
            response2 = my_gpt.get_answer_with_upload(prompt2)
            if "Not Found" not in response2:
                uspap.fields[key2] = response2

            prompt3 = "What is the subject sales and other transfers, agreements of sale, options, and listings? If you can not find, tell me Not Found."
            key3 = "the subject sales and other transfers, agreements of sale, options, and listings"
            response3 = my_gpt.get_answer_with_upload(prompt3)
            if "Not Found" not in response3:
                uspap.fields[key3] = response3

    print("======>Content<======")
    for (key, value) in uspap.fields.items():
        if value is None:
            continue
        print(key + ":")
        print(value)
    print()

    print("======>Start checking fields<======")
    print("missed fields:")
    check_required_fields(uspap)
    print()

    print("======>Start checking inconsistencies<======")
    check_inconsistencies(uspap, my_gpt, pdf_path)


if __name__ == '__main__':
    main()
