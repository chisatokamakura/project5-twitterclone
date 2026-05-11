'''
This file contains functions that work on entire documents at a time
(and not line-by-line).
'''

from markdown_compiler.util.line_functions import (
    compile_headers,
    compile_strikethrough,
    compile_bold_stars,
    compile_bold_underscore,
    compile_italic_star,
    compile_italic_underscore,
    compile_code_inline,
    compile_images,
    compile_links,
)


def compile_lines(text):
    r'''
    NOTE:
    This function calls all of the functions you created
    above to convert the full markdown file into HTML.
    This function also handles multiline markdown
    like <p> tags and <pre> tags;
    because these are multiline commands, they cannot work
    with the line-by-line style of commands above.

    NOTE:
    The doctests are divided into two sets.
    The first set of doctests below show how this
    function adds <p> tags and calls the functions above.
    Once you implement the functions above correctly,
    then this first set of doctests will pass.

    NOTE:
    For your assignment, the most important thing to take away
    from these test cases is how multiline tests can be formatted.
   '''
    lines = text.split('\n')
    new_lines = []

    in_paragraph = False
    in_code = False

    for line in lines:
        stripped = line.strip()
        if stripped == "```":   # was there a ``` ? --> close the code block
            if in_code:
                new_lines.append("</pre>")
                in_code = False
            else:
                new_lines.append("<pre>")
                in_code = True
            continue
        if in_code:
            new_lines.append(line)
            continue
        if stripped == '':
            if in_paragraph:
                new_lines.append("</p>")
                in_paragraph = False
            else:
                new_lines.append('')
            continue

        else:
            if not in_paragraph and not stripped.startswith('#'):  # '#' is heading
                new_lines.append("<p>")
                in_paragraph = True

        line = compile_headers(line)
        line = compile_strikethrough(line)
        line = compile_bold_stars(line)
        line = compile_bold_underscore(line)
        line = compile_italic_star(line)
        line = compile_italic_underscore(line)
        line = compile_code_inline(line)
        line = compile_images(line)
        line = compile_links(line)
        new_lines.append(line)
    new_text = '\n'.join(new_lines)

    return new_text


def markdown_to_html(markdown, add_css):
    '''
    Convert the input markdown into valid HTML,
    optionally adding CSS formatting.

    NOTE:
    This function is separated out from the `compile_lines`
    function so that the doctests are much simpler.
    In particular, by splitting these functions in two,
    there's no need to add all of the HTML boilerplate code to
    the doctests in `compile_lines`.

    NOTE:
    The code for this function is simple enough that we don't
    even have a "real" doctest.
    The only purpose of this doctest is to run the function and
    ensure that there are no errors.
    The `assert` function prints no output whenever
    the input is "truthy".

    >>> assert(markdown_to_html('this *is* a _test_', False))
    >>> assert(markdown_to_html('this *is* a _test_', True))
    '''

    html = '''
<html>
<head>
    <style>
    ins { text-decoration: line-through; }
    </style>
    '''
    if add_css:
        html += '''
<link rel="stylesheet" href="https://izbicki.me/css/code.css" />
<link rel="stylesheet" href="https://izbicki.me/css/default.css" />
        '''
    html += '''
</head>
<body>
    ''' + compile_lines(markdown) + '''
</body>
</html>
    '''
    return html


def minify(html):
    r'''
    Remove redundant whitespace (spaces and newlines) from the input HTML,
    and convert all whitespace characters into spaces.

    NOTE:
    When we transfer HTML files over the internet,
    we'd like them to be as small as possible in order to
    save bandwidth and make the webpage load faster.
    Minifying html documents is an important step for webservers.
    It may not seem like much, but at the scale of Google/Facebook,
    it can reduce costs by millions of dollars annually.

    >>> minify('       ')
    ''
    >>> minify('   a    ')
    'a'
    >>> minify('   a    b        c    ')
    'a b c'
    >>> minify('a b c')
    'a b c'
    >>> minify('a\nb\nc')
    'a b c'
    >>> minify('a \nb\n c')
    'a b c'
    >>> minify('a\n\n\n\n\n\n\n\n\n\n\n\n\n\nb\n\n\n\n\n\n\n\n\n\n')
    'a b'
    '''
    return " ".join(html.split())


def convert_file(input_file, add_css):
    '''
    Convert the input markdown file into an HTML file.
    If the input filename is `README.md`,
    then the output filename will be `README.html`.

    NOTE:
    It is difficult to write meaningful doctests for functions
    that deal with files.
    This is because we would have to create a bunch
    of different files to do so.
    Therefore, there are no tests for this function.
    But we can still be confident that this function will
    work because
    of the extensive tests on the "helper functions" that this
    function depends on.
    '''

    # validate that the input file is a markdown file
    if input_file[-3:] != '.md':
        raise ValueError('input_file does not end in .md')

    # load the input file
    with open(input_file, 'r') as f:
        markdown = f.read()

    # generate the HTML from the Markdown
    html = markdown_to_html(markdown, add_css)
    html = minify(html)

    # write the output file
    with open(input_file[:-2] + 'html', 'w') as f:
        f.write(html)
