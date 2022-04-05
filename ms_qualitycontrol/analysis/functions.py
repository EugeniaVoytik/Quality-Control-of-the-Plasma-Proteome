import numpy as np
import pandas as pd
from scipy import stats
import os
import re
import itertools
import statistics


def select_cols(columns):
    return 'LFQ' in columns or columns in \
        ['Gene names', 'Protein IDs', 'Protein names']


def read_own_table(filepath):
    extent = filepath.split('.')[-1]
    if extent == 'txt':
        df = pd.read_table(filepath, usecols=select_cols, low_memory=False)
    elif extent == 'csv':
        df = pd.read_csv(filepath, usecols=select_cols, low_memory=False)
    return df


def delete_uploaded_file(dir_path, filename):
    try:
        for root, dirs, files in os.walk(dir_path, topdown=False):
            os.remove(os.path.join(root, filename))
            os.rmdir(os.path.join(root, filename))
    except FileNotFoundError:
        pass


def lower_input(user_input):
    return re.findall(r"[\w']+", user_input.lower())


def get_list_of_col(df, searched_value):
    if len(searched_value) == 1:
        columns = [
            column for column in df.columns if searched_value[0]
            in column.lower()
        ]
        return columns
    elif len(searched_value) > 1:
        columns = []
        for each in searched_value:
            columns.append([
                column for column in df.columns if each in column.lower()
            ])
        return list(itertools.chain.from_iterable(columns))


def get_reversed_list_of_col(df, searched_value):
    if len(searched_value) == 1:
        columns = [
            column for column in df.columns if searched_value[0]
            not in column.lower()
        ]
        return columns
    elif len(searched_value) > 1:
        columns = []
        for each in searched_value:
            columns.append([
                column for column in df.columns if each not in column.lower()
            ])
        return list(itertools.chain.from_iterable(columns))


def two_sample_t_test(control, samples, df):
    t_stat, p_val = stats.ttest_ind(
        control,
        samples,
        axis=1,
        nan_policy='omit'
    )
    df['p_val'], df['(-)log10_p_val'] = p_val, -np.log10(p_val)
    return df


def calculate_mean(control, samples, df):
    df['control_mean'], df['samples_mean'] = np.mean(control, axis=1), \
        np.mean(samples, axis=1)
    return df


def calculate_LFC(df):
    l10fc = [np.log10(x / y) if (y != 0 and (x / y) != 0) else None
             for x, y in zip(df['samples_mean'], df['control_mean'])]
    return l10fc


def select_LFQ_cols(columns):
    return 'LFQ' in columns


def filter_valid_values(df, index, numeric_columns, percent, ax):
    df_copied = df.set_index(index)[numeric_columns]
    new_df = df_copied.dropna(
        thresh=int(len(df_copied.columns) * percent),
        axis=ax
    )
    return new_df.reset_index()


def get_list_of_indices(df, column, mask, separator):
    """
    A function that can be used for sorting of Data Frame based
    on a created list of values(mask).
    Args:
        df:  A Data Frame which we'd like to sort based on a mask.
        mask: A column based on which we'd like to sort.
        column: A list of all values that are used for sorting.
        separator: A separator based on which we'd like to split a string.

    Returns:A sorted Data Frame

    """
    indices = []
    for i in list(df[column].dropna(axis=0).index):
        proteinsIDs = df.loc[i, column].split(separator)
        if len(set(proteinsIDs).intersection(mask)) > 0:
            indices.append(i)
    return df.loc[indices]


def extract_val_from_col(df, column, separator):
    """
    This function helps to extract list of all values of a specified column.
    Args:
        df: A dataframe which we'd like to use for further sorting as a mask.
        column:  A column based on which we'd like to sort.
        separator: A separator based on which we'd like to split a string.

    Returns:A list of all values of a column.

    """
    values_protIDs = [
        value.split(separator) for value in df[column].dropna(axis=0)
    ]
    return list(itertools.chain.from_iterable(values_protIDs))


def normal_ratio(df, marker, num_std, reverse=False):
    if reverse is False:
        test = np.array(
            np.sum(marker, axis=0) / np.sum(df, axis=0),
            dtype=float
        ).round(decimals=4)
        std_bn_samples = (
            statistics.harmonic_mean(test) + np.std(test) * num_std
            ).round(decimals=4)
        return test, std_bn_samples
    else:
        test = 1/np.array(
            np.sum(marker, axis=0) / np.sum(df, axis=0), dtype=float
            ).round(decimals=4)
        std_bn_samples = (
            statistics.harmonic_mean(test) + np.std(test) * num_std
            ).round(decimals=4)
        return test, std_bn_samples


def make_annotation_item(x, y, z, color):
    return {
        'xref': 'x',
        'yref': 'y',
        'x': x,
        'y': y,
        'text': '#%s' % z.replace('LFQ', '').replace(' intensity', ''),
        'showarrow': True,
        'font': dict(family='Arial', size=12, color='white'),
        'align': 'left',
        'arrowhead': 2,
        'arrowsize': 1,
        'arrowwidth': 2,
        'arrowcolor': '#A9A9A9',
        'ax': 20,
        'ay': -30,
        'bordercolor': '#A9A9A9',
        'borderwidth': 2,
        'borderpad': 4,
        'bgcolor': color,
        'opacity': 0.8
    }


def create_annotations(data, threshold, col_names):
    data_above_threshold, data_above_threshold_indices = [], []
    for i, dd in enumerate(data):
        if dd > threshold:
            data_above_threshold.append(round(dd, 4))
            data_above_threshold_indices.append(i)
    names = [col_names[i] for i in data_above_threshold_indices]
    annotations = []
    for x, y, z in zip(
        data_above_threshold_indices,
        data_above_threshold,
        names
    ):
        annotations.append(make_annotation_item(x, y, z, '#F19F4D'))
    return annotations


def extract_markers(df, column, sort=True, top=50):
    return df.sort_values(column, ascending=sort)[:top]
