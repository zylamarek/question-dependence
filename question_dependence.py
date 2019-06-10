import pandas as pd
import numpy as np
from scipy.stats import chisquare


class QuestionDependence:
    """
    Checks if there is any association between single/multiple choice
    questions in a survey. Uses chi square test for independence.

    Parameters
    ----------
    path : str
        Path to a csv file containing survey data. Columns represent
        questions and each row specifies an answer. First row contains
        the questions in textual form. A csv file exported directly from
        Google Forms should work without any augmentation
    target : int
        Index of the question to be treated as a target. All questions
        specified in single and multi will be tested against this one.
        Target question has to be single choice. Indexing starts with 0
    single : tuple or list of ints
        List of questions indices to be treated as single choice
        questions. Indexing starts with 0
    multi : tuple or list of ints
        List of questions indices to be treated as multiple choice
        questions. Indexing starts with 0
    multi_delimiter : str
        Delimiter used in splitting multiple choice question answers
        into single data points
    min_count : int
        Minimum value of each expected frequency count for the test to
        be valid
    significance_level : float
        Threshold for p-value, below which the test's null hypothesis
        will be rejected, i.e. the questions are related

    """

    def __init__(self, path, target=-1, single=(), multi=(), multi_delimiter=',', min_count=5, significance_level=0.1):
        self.df = pd.read_csv(path).astype('category')

        if target == -1:
            target = len(self.df.columns) - 1
        self.target = target
        self.single = single
        self.multi = multi
        self.multi_delimiter = multi_delimiter
        self.min_count = min_count
        self.significance_level = significance_level

        self.target_column = self.df.iloc[:, self.target]
        self.target_categories = self.target_column.cat.categories.values
        self.n_target_categories = len(self.target_categories)
        self.target_value_counts = self.target_column.value_counts()

        self.stats = {'invalid': [],
                      'related': [],
                      'not related': []}

        self.print_info()
        self.run()
        self.print_stats()

    def print_info(self):
        print('-' * 5, 'GENERAL INFO', '-' * 5)
        print('Number of questions:', len(self.df.columns))
        print('Target question (%d): %s' % (self.target, self.target_column.name))
        print('Target question categories (%d): %s' % (self.n_target_categories, self.target_categories))
        print('Target value counts:')
        for k, v in self.target_value_counts.iteritems():
            print(k, '-', v)
        print('Significance level:', self.significance_level)
        print('Minimum expected count:', self.min_count)
        print('Single choice questions:', self.single)
        print('Multiple choice questions:', self.multi)
        print('\f', end='')

    def run(self):
        for i_question in sorted(self.single + self.multi):
            column = self.df.iloc[:, i_question]
            if i_question in self.single:
                self.analyze_question(column, self.target_column, i_question)

            elif i_question in self.multi:
                column, target_column = self.convert_multi_to_single(column)
                self.analyze_question(column, target_column, i_question)

    def print_stats(self):
        print('-' * 5, 'STATS', '-' * 5)
        print('Questions that SHOW relationship (%d): %s' % (len(self.stats['related']), self.stats['related']))
        print('Questions that DO NOT show relationship (%d): %s' % (len(self.stats['not related']),
                                                                    self.stats['not related']))
        print('Questions that render the test invalid (%d): %s' % (len(self.stats['invalid']), self.stats['invalid']))

    def analyze_question(self, column, target_column, i_question):
        print('Question', i_question)
        print(column.name)
        categories = column.cat.categories.values
        n_categories = len(categories)
        print('Categories (%d): %s' % (n_categories, categories))

        n_observed = pd.crosstab(column, target_column)
        print('Observed frequencies:')
        print(n_observed.values)

        row_sums = np.sum(n_observed.values, axis=1)
        col_sums = np.sum(n_observed.values, axis=0)
        n = sum(row_sums)
        n_expected = np.array([[row * col / n for col in col_sums] for row in row_sums])
        print('Expected frequencies:')
        with np.printoptions(precision=2):
            print(n_expected)

        if np.any(n_expected < self.min_count):
            print('Expected count too low (below %d). TEST INVALID.' % self.min_count)
            print('\f', end='')
            self.stats['invalid'].append(i_question)
            return

        # Scipy's chisquare function uses flattened data and is unable to
        # properly infer the number of degrees of freedom. We use delta
        # degrees of freedom (ddof) to adjust the value.
        # dof = k - 1 - ddof
        # k = r * c
        # ddof = r * c - 1 - (r - 1) * (c - 1)
        # ddof = r + c - 2
        # where r - number of rows and c - number of columns
        ddof = n_categories + self.n_target_categories - 2

        stat, p = chisquare(n_observed.values, n_expected, axis=None, ddof=ddof)
        print('Statistic:', stat)
        print('P-value:', p)
        print('Interpretation: ', end='')
        if p <= self.significance_level:
            print('There is a relationship between this and the target question.')
            self.stats['related'].append(i_question)
        else:
            print('There is NO relationship between this and the target question.')
            self.stats['not related'].append(i_question)

        print('\f', end='')

    def convert_multi_to_single(self, column):
        """
        In case of multiple choice questions each row is made of a list
        of answers. In order to be able to analyze this data we convert
        it into separate data points, e.g.
        ([1, 2, 3], 'Yes') -> (1, 'Yes'), (2, 'Yes'), (3, 'Yes')

        """
        df = pd.DataFrame()

        for row_data, row_target in zip(column, self.target_column):
            data = [v.strip() for v in row_data.split(self.multi_delimiter)]
            for d in data:
                df = df.append([[d, row_target]])

        df = df.astype('category')
        new_column = df.iloc[:, 0]
        target_column = df.iloc[:, 1]
        new_column.name = column.name
        return new_column, target_column
