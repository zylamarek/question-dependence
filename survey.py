import pandas as pd
import numpy as np
from scipy.stats import chisquare


class Survey():
    def __init__(self, path, target=-1, exclude=(0, 4, 7, 9, 10, 15, 17, 18, 20, 22, 26, 28)):
        self.df = pd.read_csv(path).astype('category')
        if target == -1:
            target = len(self.df.columns) - 1
        self.target = target
        self.n_target_categories = len(self.df.iloc[:, self.target].cat.categories)
        self.target_value_counts = self.df.iloc[:, self.target].value_counts()

        for i_column in range(len(self.df.columns)):
        # for i_column in range(3, 4):
            if not i_column == self.target and i_column not in exclude:
                print('-'*20)
                print(i_column)
                print(self.df.iloc[:, i_column].head(5))
                n_observed = pd.crosstab(self.df.iloc[:, i_column], self.df.iloc[:, self.target])
                print(n_observed.values)
                row_sums = np.sum(n_observed.values, axis=1)
                n_expected = [[row_sum * self.target_value_counts[k] / sum(self.target_value_counts)
                               for k in self.df.iloc[:, self.target].cat.categories] for row_sum in row_sums]
                print(n_expected)
                print(chisquare(n_observed.values, n_expected, axis=None))
