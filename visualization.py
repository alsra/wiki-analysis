import matplotlib.pyplot as plt

def main():
    pass
def mean_difference(differences):
    ''' Calculate the mean of the differences in seniority
        Input: differences - a list of differences in seniority
        Output: the mean of the differences in seniority - float
        '''
    return sum(differences) / len(differences)




def plot_histograms(ab_ba_diffs, other_reverts_diffs):
    ''' Plot histograms for the absolute differences in seniority
        Input: ab_ba_diffs - a list of absolute differences in seniority
               other_reverts_diffs - a list of absolute differences in seniority
               Output: a histogram with the two distributions overlapping - matplotlib.pyplot'''
    plt.hist(ab_ba_diffs, alpha=0.5, label='AB-BA Reverts', bins=20, density=True)
    plt.hist(other_reverts_diffs, alpha=0.5, label='Other Reverts', bins=20, density=True)
    plt.xlabel('Absolute Seniority Difference')
    plt.ylabel('Density')
    plt.title('Histogram of Absolute Seniority Differences (Density)')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
