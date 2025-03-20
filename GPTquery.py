import os
import config
from google import genai
from google.genai import types
import numpy as np


class GPTQuery:
    client = None
    file = None

    def __init__(self):
        self.client = genai.Client(api_key=config.GOOGLE_API_KEY)

    def query(self, text: str):
        response = self.client.models.generate_content(
            # model='gemini-2.0-flash',
            model='gemini-2.0-flash-lite',
            contents=text
        )
        return response.text

    def get_similarity(self, text: str):
        result = self.client.models.embed_content(
            model="text-embedding-004",
            contents=text,
            config=types.EmbedContentConfig(output_dimensionality=10),
        )
        return result.embeddings[0].values

    def upload_pdf(self, path: str):
        self.file = self.client.files.upload(file=path)

    def get_answer_with_upload(self, prompt: str):
        response = self.client.models.generate_content(
            # model="gemini-2.0-flash",
            model="gemini-2.0-flash-lite",
            contents=[prompt, self.file],
        )
        return response.text
