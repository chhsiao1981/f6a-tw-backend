# -*- coding: utf-8 -*-

from f6a_tw_backend.constants import *

import random
import math
import numpy as np
from StringIO import StringIO


def df_to_dict_list(df):
    if df is None or not len(df):
        return []

    return [dict(row) for (idx, row)in df.iterrows()]


def df_to_dict_by_idx(df):
    if df is None or not len(df):
        return {}

    return {idx: dict(row) for (idx, row) in df.iterrows()}


def df_to_csv(df, cols=None):
    if df is None or not len(df):
        return ''

    output = StringIO()
    df.to_csv(output, cols=cols, index=False)

    output_result = output.getvalue()
    output.close()

    return output_result


def agg_add_to_set(the_list):
    return set(the_list)


def _is_empty(df):
    return True if df is None or not len(df) else False
