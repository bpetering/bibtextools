import unittest
from parser import bibtex_parse, bibtex_tokenize


# https://www.economics.utoronto.ca/osborne/latex/BIBTEX.HTM
# https://www.overleaf.com/learn/latex/bibliography_management_with_bibtex
# https://www.verbosus.com/bibtex-style-examples.html
# https://www.math.uni-leipzig.de/~hellmund/LaTeX/bibtex2.pdf
# http://www.bibtex.org/Using/

# http://mirror.kumi.systems/ctan/biblio/bibtex/base/btxdoc.pdf
# http://tug.ctan.org/info/bibtex/tamethebeast/ttb_en.pdf

# http://tug.ctan.org/tex-archive/macros/latex/contrib/aguplus/sample.bib
# https://www.stat.berkeley.edu/~spector/bibtex.pdf
# https://shelah.logic.at/v1/eindex.html
# https://shelah.logic.at/v1/mybib.bib
# https://shelah.logic.at/v1/listb.bib

# https://libguides.graduateinstitute.ch/zotero/LaTex

class TestBibtexTokenize(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(bibtex_tokenize('@book'), ['book', '@'])
        self.assertEqual(bibtex_tokenize('@ book    '), ['book', '@'])

        self.assertEqual(
            bibtex_tokenize('@article{something+something96,author="Author Name",title={Title}}'),
            ['}', '}', 'Title', '{', '=', 'title', ',', '"', 'Author Name', '"', '=', 'author', ',', 'something+something96', '{', 'article', '@']
        )


    def test_complex(self):

        self.assertEqual(bibtex_tokenize(
            '@ book{ ben, author = {foo}, title={bar bat baz},      something={{double}}}'
        ), ['}', '}', '{double}', '{', '=', 'something', ',', '}', 'bar bat baz', '{', '=', 'title', ',', '}', 'foo', '{', '=', 'author', ',', 'ben', '{', 'book', '@']
        )

        self.assertEqual(
            bibtex_tokenize('''
                @STRING( EB = "Encyclopedia Britannica" )

                @book(something1995, title = 1995 # EB)
                '''),
            [')', 'EB', '#', '1995', '=', 'title', ',', 'something1995', '(', 'book', '@', ')', '"', 'Encyclopedia Britannica', '"', '=', 'EB', '(', 'STRING', '@']
        )
            

class TestBibtexParse(unittest.TestCase):

    def text_extensions_bad(self):
        # Don't generate empty dict for @string
        self.assertEqual(bibtex_parse('@string( foo = "bar" )'), [])
        self.assertEqual(bibtex_parse('@string{ bar = {something else} }  @book{hmm2000, title="really " # bar}'), [{'type': 'book', 'cite_key': 'hmm2000', 'fields': {'title': 'really something else'}}])

    def test_simple(self):
        self.assertEqual(bibtex_parse('@book{ben, author="Ben Petering", title="Bibtex Parsing"}'), 
                [{'type': 'book', 'cite_key': 'ben',
                    'fields': {'author': 'Ben Petering', 'title': 'Bibtex Parsing'}}])

    def test_multiple_basic(self):
        pass

    def test_comments(self):
        self.assertEqual(bibtex_parse('''
            foo bar bar
            @book{somebody2000, title="Book's Title", author="Somebody P. Fiddlesticks", year=2000}
        '''), [{'type': 'book', 'cite_key': 'somebody2000', 'fields': {'title': "Book's Title", 'author': 'Somebody P. Fiddlesticks', 'year': 2000}}]
        )

        s = '''
        book{somebody2000, 
            title = "Foo",
            author = {Bar bat baz},
            somethingelse = {{ fiddlesticks }} ,
        }
        blah
        @article { authors1000000000, 
            title={Article About Something},
            authors={People}
        }
        '''
        # Only 1 entry - other "commented out" by removing @
        self.assertEqual(bibtex_parse(s),
                [{'type': 'article', 'cite_key': 'authors1000000000', 'fields': {
                    'title': 'Article About Something',
                    'authors': 'People'
                }}]
        )

        s = '''
        A bunch of random junk that's a comment "{"}{} 

        @article { authors1000000000, 
            title={Article About Something},
            authors={People}
        }yoyoyoyoyoyoyoyoyo #$%^#$%^#$&#^*&#$%^&{}{}{}{}(()()()()

        @BOOK( COOLAUTHOR2000, title = "COOL TITLE" )psidfo;iah;fha;sdhfaousgdfgasldigf }{}{}{

        @book{another2020,title="cooler title", authors={{fiddlesticks and friends}}
        }
        something
        '''
        self.assertEqual(bibtex_parse(s), [
            {'type': 'article', 'cite_key': 'authors1000000000', 'fields': {
                'title': 'Article About Something',
                'authors': 'People'
            }},
            {'type': 'book', 'cite_key': 'coolauthor2000', 'fields': {
                'title': 'COOL TITLE'
            }},
            {'type': 'book', 'cite_key': 'another2020', 'fields': {
                'title': 'cooler title', 
                'authors': '{fiddlesticks and friends}'
            }}
        ])

    def test_full(self):
        s = '''@article{bloom_oligopoly_2016,
            title = {The {Oligopoly} of {Large} {Mammals} in the {Digital} {Era}},
            volume = {12},
            doi = {10.1234/journal.pone.012345},
            language = {en},
            number = {7},
            journal = {PLOS ONE},
            author = {Bloom, Vincent and Andrews, Stefanie and Bernard, Philippe},
            month = "jun",
            year = {2016},
            pages = {e012345}
        }
        '''
        self.assertEqual(bibtex_parse(s), [{
            'type': 'article',
            'cite_key': 'bloom_oligopoly_2016',
            'fields': {
                'title': 'The {Oligopoly} of {Large} {Mammals} in the {Digital} {Era}',
                'author': 'Bloom, Vincent and Andrews, Stefanie and Bernard, Philippe',
                'volume': '12',
                'doi': '10.1234/journal.pone.012345',
                'language': 'en',
                'number': '7',
                'journal': 'PLOS ONE',
                'month': 'jun',
                'year': '2016',
                'pages': 'e012345'
            }}]
        )

        s = '''
            @article{Fiddlesticks:1178,
            author = {Smith, John and Celeste, Mary and Jones, Davy},
            trueauthor = {Smith, John and Celeste, Mary and Jones, Davy},
            fromwhere = {CA,CA,CA},
            journal = {preprint},
            title = {Dangerous Sea Excursions}
        }
        '''
        
        self.assertEqual(bibtex_parse(s), [{
            'type': 'article',
            'cite_key': 'Fiddlesticks:1178',
            'fields': {
                'author': 'Smith, John and Celeste, Mary and Jones, Davy',
                'trueauthor': 'Smith, John and Celeste, Mary and Jones, Davy',
                'fromwhere': 'CA,CA,CA',
                'journal': 'preprint',
                'title': 'Dangerous Sea Excursions'
            }
        }]
        )

    def test_whole_file(self):
        pass

    def test_extensions(self):
        s = '''
                @STRING( EB = "Encyclopedia Britannica" )

                @book(something1995, title = 1995 # EB)
        '''
        self.assertEqual(bibtex_parse(s), [{
            'type': 'book',
            'cite_key': 'something1995',
            'fields': {
                'title': '1995 Encyclopedia Britannica'
            }
        }]
        )

if __name__ == '__main__':
    unittest.main()


