import os.path
from unittest import TestCase

import pdfrw

from pdf_annotate import Appearance
from pdf_annotate import Location
from pdf_annotate import PdfAnnotator
from tests.files import PNG_FILES
from tests.files import ROTATED_180
from tests.files import ROTATED_270
from tests.files import ROTATED_90
from tests.files import SIMPLE


class EndToEndMixin(object):
    """End to end test of PdfAnnotator.

    To truly test PDF annotations end to end, you need to do some sort of
    visual inspection. There are several options, including rastering the PDF
    and doing pixel diffs. Until we end up doing something like this, the end-
    to-end test will be a tiny amount of validation in code + manual inspection
    of the output.
    """

    def setUp(self):
        self.gaudy = Appearance(
            stroke_color=[1, 0, 0],
            stroke_width=3,
            fill=[0, 1, 0],
            content='Latin',
            font_size=12,
            wrap_text=True,
        )

        self.transparent = self.gaudy.copy(
            fill=[0, 0, 1, 0.5],
            stroke_color=[1, 0, 0, 0.25],
        )

        self.top_left = self.gaudy.copy(
            stroke_color=[0, 0, 0],
            content=(
                r"Though yet of Hamlet, our dear brother's death \\ "
                r"The memory be green"
            ),
            font_size=6,
            text_align='left',
            text_baseline='top',
        )
        self.top_center = self.top_left.copy(text_align='center')
        self.top_right = self.top_left.copy(text_align='right')

        self.middle_left = self.top_left.copy(text_baseline='middle')
        self.middle_center = self.middle_left.copy(text_align='center')
        self.middle_right = self.middle_left.copy(text_align='right')

        self.bottom_left = self.top_left.copy(text_baseline='bottom')
        self.bottom_center = self.bottom_left.copy(text_align='center')
        self.bottom_right = self.bottom_left.copy(text_align='right')

        self.texts = [
            self.top_left, self.top_center, self.top_right,
            self.middle_left, self.middle_center, self.middle_right,
            self.bottom_left, self.bottom_center, self.bottom_right,
        ]

        self.image_appearance = Appearance(stroke_width=0)
        self.transparent_image_appearance = self.image_appearance.copy(
            fill_transparency=0.5,
            stroke_transparency=0.5,
        )

    def test_end_to_end(self):
        a = PdfAnnotator(self.INPUT_FILENAME)
        self._add_annotations(a)
        output_file = self._get_output_file()
        a.write(output_file)
        self._check_num_annotations(output_file)

    def _check_num_annotations(self, output_file):
        f = pdfrw.PdfReader(output_file)
        assert len(f.pages[0].Annots) == 29

    def _get_output_file(self):
        dirname, _ = os.path.split(os.path.abspath(__file__))
        return os.path.join(dirname, 'pdfs', self.OUTPUT_FILENAME)

    def _add_annotations(self, a):
        self._add_shape_annotations(a, self.gaudy)
        self._add_shape_annotations(a, self.transparent, y1=70, y2=110)
        self._add_image_annotations(a, self.image_appearance)
        self._add_image_annotations(
            a,
            self.transparent_image_appearance,
            y1=170,
            y2=210,
        )
        self._add_text_annotations(a)

    def _add_shape_annotations(self, a, appearance, y1=20, y2=60):
        a.add_annotation(
            'square',
            Location(x1=10, y1=y1, x2=50, y2=y2, page=0),
            appearance,
        )
        a.add_annotation(
            'circle',
            Location(x1=60, y1=y1, x2=100, y2=y2, page=0),
            appearance,
        )
        a.add_annotation(
            'polygon',
            Location(points=[[110, y1], [150, y1], [130, y2]], page=0),
            appearance,
        )
        a.add_annotation(
            'polyline',
            Location(points=[[160, y1], [200, y1], [180, y2]], page=0),
            appearance,
        )
        a.add_annotation(
            'line',
            Location(points=[[210, y1], [250, y2]], page=0),
            appearance,
        )
        a.add_annotation(
            'ink',
            Location(points=[[260, y1], [300, y2]], page=0),
            appearance,
        )

    def _add_image_annotations(self, a, appearance, y1=120, y2=160):
        xs = [10, 60, 110, 160]
        for x, image_file in zip(xs, PNG_FILES):
            a.add_annotation(
                'image',
                Location(x1=x, y1=y1, x2=(x + 40), y2=y2, page=0),
                appearance.copy(image=image_file),
            )

    def _add_text_annotations(self, a, y1=220, y2=300):
        xs = [10 + (i * 50) for i in range(len(self.texts))]
        for x, appearance in zip(xs, self.texts):
            a.add_annotation(
                'text',
                Location(x1=x, y1=y1, x2=(x + 40), y2=y2, page=0),
                appearance,
            )


class TestEndToEnd(EndToEndMixin, TestCase):
    INPUT_FILENAME = SIMPLE
    OUTPUT_FILENAME = 'end_to_end.pdf'


class TestEndToEndRotated90(EndToEndMixin, TestCase):
    INPUT_FILENAME = ROTATED_90
    OUTPUT_FILENAME = 'end_to_end_rotated_90.pdf'


class TestEndToEndRotated180(EndToEndMixin, TestCase):
    INPUT_FILENAME = ROTATED_180
    OUTPUT_FILENAME = 'end_to_end_rotated_180.pdf'


class TestEndToEndRotated270(EndToEndMixin, TestCase):
    INPUT_FILENAME = ROTATED_270
    OUTPUT_FILENAME = 'end_to_end_rotated_270.pdf'
