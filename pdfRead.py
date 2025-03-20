import pymupdf
import os
import importlib

import GreenFormat
from Format import Format
# from GreenFormat import Title1Attribute, Title2Attribute, BodyAttribute
# from WhiteFormat import Title1Attribute, Title2Attribute, BodyAttribute

from MyTitle import Title


class ReadPDF:
    pdf = None
    content = dict()
    content_title1 = dict()
    certification = None

    pdf_format = None

    def __init__(self, pdf_path, format):
        self.pdf: pymupdf.Document = pymupdf.open(pdf_path)
        if format == 1:
            self.pdf_format = importlib.import_module("GreenFormat")
        else:
            self.pdf_format = importlib.import_module("WhiteFormat")

    def is_title(self, font_color: tuple, font_size: float, font_name: str):
        """
        :param font_color:
        :param font_size:
        :param font_name:
        :return: if content matched Title1Attribute or Title2Attribute, return True, else False
        """
        if (self.is_format_match(self.pdf_format.Title1Attribute(), font_color, font_size, font_name)
                or self.is_format_match(self.pdf_format.Title2Attribute(), font_color, font_size, font_name)):
            return True
        return False

    @staticmethod
    def is_format_match(attr: Format, font_color: tuple, font_size: float, font_name: str):
        """
        :param attr:
        :param font_color:
        :param font_size:
        :param font_name:
        :return: if the content matched target Format-> True, else False
        """
        if (font_color == attr.get_font_color()
                and attr.get_font_size_min() <= font_size <= attr.font_size_max
                and font_name == attr.get_font_name()):
            return True
        else:
            return False

    @staticmethod
    def save_image(block: dict):
        print(block["ext"])
        print(block["xres"])
        with open("temp.{}".format(block["ext"]), 'wb') as f:
            f.write(block["image"])

    def read_until_next_title(self, title: Title):
        is_find = False
        for page in self.pdf.pages(title.page_number, self.pdf.page_count, 1):
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        size = span["size"]
                        font = span["font"]
                        color = pymupdf.sRGB_to_rgb(span["color"])
                        # print(f"text: {text}, size: {size}, color: {color}")
                        if not is_find and text.strip() == title.text:
                            is_find = True
                            continue
                        if is_find:
                            if self.is_title(color, size, font):
                                return
                            if self.is_format_match(self.pdf_format.BodyAttribute(), color, size, font):
                                title.content_text += text

    def get_titles(self):
        # for page in self.pdf.pages(3, self.pdf.page_count, 1):
        #     blocks = page.get_text("dict")["blocks"]
        # for page_number in range(4, self.pdf.page_count):
        for page_number in range(3, self.pdf.page_count):
            page: pymupdf.Page = self.pdf[page_number]
            blocks: list = page.get_text("dict")["blocks"]

            for block in blocks:
                # image block
                if "type" in block and block["type"] == 1:
                    continue
                else:
                    if "lines" not in block:
                        # print(block["lines"])
                        continue
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            size = span["size"]
                            font = span["font"]
                            # bbox (x0, y0, x1, y1)
                            y = span["bbox"][1]
                            color = pymupdf.sRGB_to_rgb(span["color"])
                            # print(f"text: {text}, size: {size}, color: {color}")
                            if self.is_format_match(self.pdf_format.Title2Attribute(), color, size, font):
                                self.content[text] = Title(page_number, y, text)
                            elif self.is_format_match(self.pdf_format.Title1Attribute(), color, size, font):
                                self.content_title1[text] = Title(page_number, y, text)

    def get_page(self, target_field):
        pages = [0, 0]

        for key in self.content_title1.keys():
            if key.lower() == target_field:
                title: Title = self.content_title1[key]
                pages[0] = title.page_number
                is_find = False
                for page in self.pdf.pages(title.page_number, self.pdf.page_count, 1):
                    blocks = page.get_text("dict")["blocks"]

                    for block in blocks:
                        if "lines" not in block:
                            continue
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"]
                                size = span["size"]
                                font = span["font"]
                                color = pymupdf.sRGB_to_rgb(span["color"])
                                # print(f"text: {text}, size: {size}, color: {color}")
                                if not is_find and text.strip() == title.text:
                                    is_find = True
                                    continue
                                if is_find:
                                    if self.is_title(color, size, font):
                                        pages[1] = page.number
                                        return pages
            elif key.lower() == target_field:
                title: Title = self.content_title1[key]
                pages[0] = title.page_number
                is_find = False
        return pages

    def read_pdf(self):
        self.get_titles()
        for title in self.content.keys():
            self.read_until_next_title(self.content[title])
