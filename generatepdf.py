from fpdf import FPDF


class Pdf:
    def __int__(self):
        self.pdf = None

    def create_page(self):
        self.pdf = FPDF()

    def set_fonts(self, font_size, font_style):
        self.pdf.add_page()
        self.pdf.set_font(font_style, size=font_size)

    def write_page(self, words, align):
        self.pdf.cell(200, 10, txt=words, ln=1, align=align)

    def generate(self, name):
        return self.pdf.output(f'{name}.pdf')