class Title:
    page_number = int()
    y = float()
    text = str()
    content_text = str()
    content_table = str()
    content_img = str()

    def __init__(self, page_number, y, text):
        self.page_number = page_number
        self.y = y
        self.text = text

    def get_page_number(self):
        return self.page_number

    def get_y(self):
        return self.y

    def get_content(self):
        return self.content
