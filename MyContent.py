
class MyContent:
    title = str()
    text = str()
    table = str()
    img = dict()

    def set_title(self, title: str):
        self.title = title

    def get_title(self):
        return self.title

    def set_text(self, text: str):
        self.text = text

    def get_text(self):
        return self.text

    def set_table(self, table: str):
        self.table = table

    def get_table(self):
        return self.table

    def set_img(self, img: dict):
        self.img = img

    def get_img(self):
        return self.img



