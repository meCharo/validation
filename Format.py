class Format:
    font_color = tuple()
    font_size_min = int()
    font_size_max = int()
    font_name = str()

    def get_font_size_min(self):
        return self.font_size_min

    def get_font_size_max(self):
        return self.font_size_max

    def get_font_color(self):
        return self.font_color

    def get_font_name(self):
        return self.font_name
