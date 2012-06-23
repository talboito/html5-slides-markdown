#! /usr/bin/env python

import codecs
import re
import jinja2
import markdown2 as markdown
import pygments

from optparse import OptionParser

from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def make_slides(inpath, outpath, templatepath, encoding):
    with codecs.open(outpath, 'w', encoding=encoding) as outfile:
        md_src = codecs.open(inpath, encoding=encoding).read()
        slides_src = markdown.markdown(md_src).split('<hr />\n')

        title = slides_src.pop(0)

        head_title = title.split('>')[1].split('<')[0]

        slides = parse_slides(slides_src)

        template = jinja2.Template(open(templatepath).read())
        outfile.write(template.render(locals()))

def parse_slides(slides_src):
    slides = []
    for slide_src in slides_src:
        header, content = slide_src.split('\n', 1)

        while '<code>!' in content:
            content = parse_code(content)

        slides.append({'header': header, 'content': content})

    return slides

def parse_code(content):
    lang_match = re.search('<code>!(.+)\n', content)

    if lang_match:
        lang = lang_match.group(1)
        code = content.split(lang, 1)[1].split('</code', 1)[0]

        lexer = get_lexer_by_name(lang)

        formatter = HtmlFormatter(linenos='inline', noclasses=True,
                                              nobackground=True)

        pretty_code = pygments.highlight(code, lexer, formatter)
        pretty_code = pretty_code.replace('&amp;', '&')

        before_code = content.split('<code>', 1)[0]
        after_code = content.split('</code>', 1)[1]

        content = before_code + pretty_code + after_code

    return content

def main():
    option_parser = OptionParser()

    option_parser.add_option('-s', '--source', action = 'store',
                             help = 'The path to the markdown source file; default is "%default"',
                             dest = 'source', nargs = 1, default = 'slides.md', metavar = 'FILE')

    option_parser.add_option('-d', '--destination', action = 'store',
                             help = 'The path to the destination file; default is "%default"',
                             dest = 'destination', nargs = 1, default = 'presentation.html', metavar = 'FILE')

    option_parser.add_option('-t', '--template', action = 'store',
                             help = 'The path to the Jinja2 template file; default is "%default"',
                             dest = 'template', nargs = 1, default = 'base.html', metavar = 'FILE')

    option_parser.add_option('-e', '--encoding', action = 'store',
                             help = 'The file encoding to use; default is "%default"',
                             dest = 'encoding', nargs = 1, default = 'utf8', metavar = 'ENCODING')

    (options, args) = option_parser.parse_args()

    make_slides(options.source,
                options.destination,
                options.template,
                options.encoding)

if __name__ == '__main__':
    main()
