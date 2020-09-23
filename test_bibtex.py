import unittest
from bibtex import bibtex_parse, bibtex_tokenize


# https://www.economics.utoronto.ca/osborne/latex/BIBTEX.HTM
# https://www.overleaf.com/learn/latex/bibliography_management_with_bibtex
# https://www.verbosus.com/bibtex-style-examples.html
# https://www.math.uni-leipzig.de/~hellmund/LaTeX/bibtex2.pdf
# http://www.bibtex.org/Using/

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


class TestBibtexParse(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(bibtex_parse('@book{ben, author="Ben Petering", title="Bibtex Parsing"}'), 
                [{'type': 'book', 'cite_key': 'ben',
                    'fields': {'author': 'Ben Petering', 'title': 'Bibtex Parsing'}}])

    def test_multiple_basic(self):
        pass

    def test_full(self):
        s = '''@article{bloom_oligopoly_2016,
            title = {The {Oligopoly} of {Large} {Mammals} in the {Digital} {Era}},
            volume = {12},
            doi = {10.1234/journal.pone.012345},
            language = {en},
            number = {7},
            journal = {PLOS ONE},
            author = {Bloom, Vincent and Andrews, Stefanie and Bernard, Philippe},
            month = jun,
            year = {2016},
            pages = {e012345},
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
            }}]);

        s = '''
            @article{Fiddlesticks:1178,
            author = {Smith, John and Jones, Indiana and Jones, Davy},
            trueauthor = {Smith, John and Jones, Indiana and Jones, Davy},
            fromwhere = {CA,CA,CA},
            journal = {preprint},
            title = {{Dangerous Archaeology: Land and Sea}},
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
        }])

if __name__ == '__main__':
    unittest.main()


