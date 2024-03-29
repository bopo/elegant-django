from django.templatetags.static import static
from django.test import TestCase
from django.utils.translation import gettext as _

from elegant import utils
from elegant.widgets import LinkedSelect, HTML5Input, EnclosedInput, \
    NumberInput, ElegantDateWidget, ElegantTimeWidget, ElegantSplitDateTimeWidget, \
    AutosizedTextarea

django_version = utils.django_major_version()


class WidgetsTestCase(TestCase):
    def test_NumberInput(self):
        inp = NumberInput()
        self.assertEqual('number', inp.input_type)

    def test_HTML5Input(self):
        input_type = 'calendar'
        inp = HTML5Input(input_type=input_type)
        self.assertEqual(input_type, inp.input_type)

    def test_LinkedSelect(self):
        ls = LinkedSelect()
        self.assertTrue('linked-select' in ls.attrs['class'])

    def test_LinkedSelect_with_existing_attr(self):
        ls = LinkedSelect(attrs={'class': 'custom-class', 'custom': 123})
        self.assertEqual('linked-select custom-class', ls.attrs['class'])
        self.assertEqual(ls.attrs['custom'], 123)

    def render_enclosed_widget(self, enclosed_widget):
        return enclosed_widget.render('enc', 123)

    def get_enclosed_widget_html(self, values):
        return '<div class="input-prepend input-append">%s<input name="enc" ' \
               'type="text" value="123" />%s</div>' % values

    def test_EnclosedInput_as_text(self):
        inp = EnclosedInput(prepend='p', append='a')
        output = self.render_enclosed_widget(inp)
        result = ('<span class="add-on">p</span>',
                  '<span class="add-on">a</span>')
        self.assertHTMLEqual(output, self.get_enclosed_widget_html(result))

    def test_EnclosedInput_as_icon(self):
        inp = EnclosedInput(prepend='icon-fire', append='icon-leaf')
        output = self.render_enclosed_widget(inp)
        result = ('<span class="add-on"><i class="icon-fire"></i></span>',
                  '<span class="add-on"><i class="icon-leaf"></i></span>')
        self.assertHTMLEqual(output, self.get_enclosed_widget_html(result))

    def test_EnclosedInput_as_html(self):
        inp = EnclosedInput(prepend='<em>p</em>', append='<em>a</em>')
        output = self.render_enclosed_widget(inp)
        result = ('<em>p</em>', '<em>a</em>')
        self.assertHTMLEqual(output, self.get_enclosed_widget_html(result))

    def test_ElegantDateWidget(self):
        sdw = ElegantDateWidget()
        self.assertTrue('vDateField' in sdw.attrs['class'])

    def test_ElegantDateWidget_with_existing_class_attr(self):
        sdw = ElegantDateWidget(attrs={'class': 'custom-class'})
        self.assertTrue('vDateField ' in sdw.attrs['class'])
        self.assertTrue(' custom-class' in sdw.attrs['class'])
        self.assertEqual(_('Date:')[:-1], sdw.attrs['placeholder'])

    def test_ElegantDateWidget_with_existing_placeholder_attr(self):
        sdw = ElegantDateWidget(attrs={'class': 'custom-cls', 'placeholder': 'p'})
        self.assertTrue('vDateField ' in sdw.attrs['class'])
        self.assertTrue(' custom-cls' in sdw.attrs['class'])
        self.assertEqual('p', sdw.attrs['placeholder'])

    def get_ElegantDateWidget_output(self):
        if django_version < (1, 11):
            return '<div class="input-append elegant-date"><input class="vDateField ' \
                   'input-small " name="sdw" placeholder="Date" ' \
                   'size="10" type="text" /><span class="add-on"><i ' \
                   'class="icon-calendar"></i></span></div>'
        elif django_version < (3, 0):
            return '<div class="input-append elegant-date"><input type="text" name="sdw" ' \
                   'value="" class="vDateField input-small " size="10" placeholder="Date" />' \
                   '<span class="add-on"><i class="icon-calendar"></i></span></div>'
        else:
            return '<div class="input-append elegant-date"><input type="text" name="sdw" ' \
                   'value="" class="vDateField input-small " size="10" placeholder="Date" />' \
                   '<span class="add-on"><i class="icon-calendar"></i></span></div>'

    def test_ElegantDateWidget_output(self):
        sdw = ElegantDateWidget(attrs={'placeholder': 'Date'})
        output = sdw.render('sdw', '')

        self.assertHTMLEqual(self.get_ElegantDateWidget_output(), output, msg=output)

    def test_ElegantTimeWidget(self):
        sdw = ElegantTimeWidget()
        self.assertTrue('vTimeField' in sdw.attrs['class'])

    def test_ElegantTimeWidget_with_existing_class_attr(self):
        sdw = ElegantTimeWidget(attrs={'class': 'custom-class'})
        self.assertTrue('vTimeField ' in sdw.attrs['class'])
        self.assertTrue(' custom-class' in sdw.attrs['class'])
        self.assertEqual(_('Time:')[:-1], sdw.attrs['placeholder'])

    def test_ElegantTimeWidget_with_existing_placeholder_attr(self):
        sdw = ElegantTimeWidget(attrs={'class': 'custom-cls', 'placeholder': 'p'})
        self.assertTrue('vTimeField ' in sdw.attrs['class'])
        self.assertTrue(' custom-cls' in sdw.attrs['class'])
        self.assertEqual('p', sdw.attrs['placeholder'])

    def get_ElegantTimeWidget_output(self):
        if django_version < (1, 11):
            return '<div class="input-append elegant-date elegant-time"><input ' \
                   'class="vTimeField input-small " name="sdw" ' \
                   'placeholder="Time" size="8" type="text" /><span ' \
                   'class="add-on"><i class="icon-time"></i></span></div>'
        else:
            return '<div class="input-append elegant-date elegant-time"><input ' \
                   'type="text" name="sdw" value="" class="vTimeField input-small " ' \
                   'size="8" placeholder="Time" /><span class="add-on">' \
                   '<i class="icon-time"></i></span></div>'

    def test_ElegantTimeWidget_output(self):
        sdw = ElegantTimeWidget(attrs={'placeholder': 'Time'})
        output = sdw.render('sdw', '')
        self.assertHTMLEqual(
            self.get_ElegantTimeWidget_output(),
            output)

    def get_ElegantSplitDateTimeWidget_output(self):
        if django_version < (1, 11):
            dwo = self.get_ElegantDateWidget_output().replace('sdw', 'sdw_0')
            two = self.get_ElegantTimeWidget_output().replace('sdw', 'sdw_1')
            return '<div class="datetime">%s %s</div>' % (dwo, two)
        elif django_version > (4, 1):
            return ('<div class="input-append elegant-date"><input type="text" name="sdw_0" '
                    'class="vDateField input-small " size="10" placeholder="Date">'
                    '<span class="add-on"><i class="icon-calendar"></i></span></div>'
                    '<div class="input-append elegant-date elegant-time">'
                    '<input type="text" name="sdw_1" class="vTimeField input-small " size="8" placeholder="Time">'
                    '<span class="add-on"><i class="icon-time"></i></span></div>')
        else:
            return '<div class="datetime"><input type="text" name="sdw_0" ' \
                   'class="vDateField input-small " size="10" placeholder="Date" ' \
                   '/><input type="text" name="sdw_1" class="vTimeField input-small " ' \
                   'size="8" placeholder="Time" /></div>'

    def test_ElegantSplitDateTimeWidget(self):
        ssdtw = ElegantSplitDateTimeWidget()
        output = ssdtw.render('sdw', '')
        self.assertHTMLEqual(self.get_ElegantSplitDateTimeWidget_output(), output)

    def test_AutosizedTextarea(self):
        txt = AutosizedTextarea()
        self.assertTrue('autosize' in txt.attrs['class'])
        self.assertEqual(2, txt.attrs['rows'])

    def test_AutosizedTextarea_with_existing_attrs(self):
        txt = AutosizedTextarea(attrs={'class': 'custom-class', 'rows': 3})
        self.assertTrue('autosize ' in txt.attrs['class'])
        self.assertTrue(' custom-class' in txt.attrs['class'])
        self.assertEqual(txt.attrs['rows'], 3)

    def test_AutosizedTextarea_output(self):
        txt = AutosizedTextarea()
        self.assertHTMLEqual(txt.render('txt', ''), (
            '<textarea class="autosize " cols="40" name="txt" '
            'rows="2">\r\n</textarea><script type="text/javascript">Elegant.$('
            '\'#id_txt\').autosize();</script>'))

    def test_AutosizedTextarea_media(self):
        txt = AutosizedTextarea()
        js_url = static('elegant/js/jquery.autosize-min.js')

        # self.assertHTMLEqual(str(txt.media), f'<script src="{js_url}"></script>')
        self.assertIn(f'src="{js_url}"', str(txt.media))
