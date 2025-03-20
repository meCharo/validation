import pymupdf
import os

from Format import Format, Title1Attribute, Title2Attribute, BodyAttribute
from google import genai

from MyContent import MyContent


# document-based chucking


class Title:
    page_number = int()
    y = float()
    content = str()

    def __init__(self, page_number, y, content):
        self.page_number = page_number
        self.y = y
        self.content = content

    def get_page_number(self):
        return self.page_number

    def get_y(self):
        return self.y

    def get_content(self):
        return self.content


def is_format_match(attr: Format, font_color: tuple, font_size: float, font_name: str):
    """
    :param attr:
    :param font_color:
    :param font_size:
    :param font_name:
    :return: if the content matched target Format-> True, else False
    """
    if (font_color == attr.get_font_color()
            and attr.get_font_size_min() < font_size < attr.font_size_max
            and font_name == attr.get_font_name()):
        return True
    else:
        return False


def get_titles(pdf: pymupdf.Document):
    """
    :param pdf:
    :return: titles, including all titles in the pdf. titles["title1"]...
    """
    titles = dict()
    title1 = list()
    title2 = list()
    titles["title1"] = title1
    titles["title2"] = title2

    index = 0

    for page_number in range(4, pdf.page_count):
        # for page_number in range(3, pdf.page_count):
        page = pdf[page_number]
        blocks = page.get_text("dict")["blocks"]  # make sure block is a dict

        # get font size, color, and content
        for block in blocks:
            index += 1
            print(block)
            # if "type" in block and block["type"] == 1:
            #     print(block)
            # if "block_type" in block and block["block_type"] == 1:
            #     print(block)
            # else:
            #     print()
            if index == 3:
                exit()

            if "lines" not in block:
                continue
            for line in block["lines"]:
                # print(line)
                for span in line["spans"]:
                    text = span["text"].strip()  # only needed for a title
                    size = span["size"]
                    font = span["font"]
                    color = pymupdf.sRGB_to_rgb(span["color"])
                    # bbox (x0, y0, x1, y1)
                    y = span["bbox"][1]
                    # print(f"text: {text}, size: {size}, color: {color}")
                    if is_format_match(Title1Attribute(), color, size, font):
                        title1.append(Title(page_number, y, text))
                    if is_format_match(Title2Attribute(), color, size, font):
                        title2.append(Title(page_number, y, text))
    return titles


def is_title(font_color: tuple, font_size: float, font_name: str):
    """
    :param font_color:
    :param font_size:
    :param font_name:
    :return: if content matched Title1Attribute or Title2Attribute, return True, else False
    """
    if (is_format_match(Title1Attribute(), font_color, font_size, font_name)
            or is_format_match(Title2Attribute(), font_color, font_size, font_name)):
        return True
    return False


def find_images(pdf: pymupdf.Document, title: Title):
    images = list()

    for i in range(title.page_number, pdf.page_count):
        page = pdf[i]
        images_page = page.get_images(full=True)

        # title page
        if i == title.page_number:
            if len(images_page) != 0:
                for img in images_page:
                    # xref, smask, ...
                    xref = img[0]
                    # Rect: x, y, width, height
                    if img[1] > title.y:
                        images.append(pymupdf.Pixmap(pdf, xref))
            continue

        # find next title first
        blocks = page.get_text("dict")["blocks"]
        # title-> compare y with img
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    size = span["size"]
                    font = span["font"]
                    # bbox (x0, y0, x1, y1)
                    y = span["bbox"][1]
                    color = pymupdf.sRGB_to_rgb(span["color"])
                    if is_title(color, size, font):
                        if len(images_page) != 0:
                            for img in images_page:
                                # xref, smask, ...
                                xref = img[0]
                                # Rect: x, y, width, height
                                if img[1] < y:
                                    images.append(pymupdf.Pixmap(pdf, xref))
                        return images

        # no title-> add img
        if len(images_page) != 0:
            for img in images_page:
                # xref, smask, ...
                xref = img[0]
                images.append(pymupdf.Pixmap(pdf, xref))
    print("can not find next title")
    return images


def find_tables(pdf: pymupdf.Document, title: Title):
    tables = list()
    # print(title.page_number)

    for i in range(title.page_number, pdf.page_count):
        page = pdf[i]
        tables_page = page.find_tables(strategy="text")
        for table in tables_page:
            print(table.extract())
        print(tables_page)
        break

    # import pdfplumber
    # pdf_path = r"20220614 - 3020 Wilshire - CBRE Land Appraisal - Valuation.pdf"
    # with pdfplumber.open(pdf_path) as pdf_file:
    #     for i in range(title.page_number, pdf.page_count):
    #         page = pdf_file.pages[i]
    #         table = page.extract_table(table_settings={
    #             'vertical_strategy': "text",
    #             "horizontal_strategy": "text"})
    #         print(table)
    #         break

    """
    title of table: last Three/four/five (depends on field line and two line value)
    size = 9.409788131713867
    color = 0
    font = FuturaBT-Bold
    
    Source: before the title of table
    size = 7.712940692901611
    color = 0
    font: FuturaBT-Medium
    
    body:
    size = 8.587140083312988
    color = 0
    font: FuturaBT-Medium
    
    find upper and lower boundary (is there always a blank block after a table?)
    case1: upper body, lower body
    case2: upper title, lower title
    case3:
    case4:
    (may include img)
    
    is the value in tables important?
    not-> get the boundary and save as a picture and send to gpt
    yes-> find field and save
    """

    # for page in pdf.pages(title.page_number, pdf.page_count, 1):
    #     blocks = page.get_text("dict")["blocks"]
    #     # print(page.get_text("dict"))
    #
    #     for block in blocks:
    #         print()
    #         print(block)
    #         if "lines" not in block:
    #             continue
    #
    #         for line in block["lines"]:
    #             for span in line["spans"]:
    #                 text = span["text"]
    #                 size = span["size"]
    #                 font = span["font"]
    #                 color = pymupdf.sRGB_to_rgb(span["color"])
    #                 # print(f"text: {text}, size: {size}, color: {color}, font: {font}")
    #     break


def find_text(pdf: pymupdf.Document, title: Title):
    text_res = str()

    is_find = False
    for page in pdf.pages(title.page_number, pdf.page_count, 1):
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            print(block)
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    size = span["size"]
                    font = span["font"]
                    color = pymupdf.sRGB_to_rgb(span["color"])
                    # print(f"text: {text}, size: {size}, color: {color}")
                    if not is_find and text.strip() == title.content:
                        is_find = True
                        continue
                    if is_find:
                        if is_title(color, size, font):
                            return text_res
                        if not is_format_match(BodyAttribute(), color, size, font):
                            continue
                        if is_find:
                            text_res += span["text"]
    print("can not find the next title")
    exit(0)


def read_until_title(pdf: pymupdf.Document, title: Title):
    contents = dict()

    contents["text"] = find_text(pdf, title)
    contents["tables"] = find_tables(pdf, title)
    contents["images"] = find_images(pdf, title)

    return contents


class ReadPDF:
    pdf = pymupdf.Document()

    def __init__(self, pdf_path):
        self.pdf = pymupdf.open(pdf_path)

    @staticmethod
    def is_title(font_color: tuple, font_size: float, font_name: str):
        """
        :param font_color:
        :param font_size:
        :param font_name:
        :return: if content matched Title1Attribute or Title2Attribute, return True, else False
        """
        if (is_format_match(Title1Attribute(), font_color, font_size, font_name)
                or is_format_match(Title2Attribute(), font_color, font_size, font_name)):
            return True
        return False

    def read_whole(self):
        contents = list()

        for page_number in range(4, self.pdf.page_count):
            # for page_number in range(3, pdf.page_count):
            page = self.pdf[page_number]
            blocks = page.get_text("dict")["blocks"]  # make sure block is a dict

            for block in blocks:
                # image block
                if "type" in block and block["type"] == 1:
                    print(block)

def read_whole(pdf: pymupdf.Document):
    contents = list()
    for page_number in range(4, pdf.page_count):
        # for page_number in range(3, pdf.page_count):
        page = pdf[page_number]
        blocks = page.get_text("dict")["blocks"]  # make sure block is a dict

        for block in blocks:
            # image block
            if "type" in block and block["type"] == 1:
                print(block)

        break


    return contents


# def main():
#     pdf_path = r"20220614 - 3020 Wilshire - CBRE Land Appraisal - Valuation.pdf"
#     pdf = pymupdf.open(pdf_path)
#     titles = get_titles(pdf)
#
#
#
#
# if __name__ == '__main__':
#     main()
