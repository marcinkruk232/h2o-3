# -*- encoding: utf-8 -*-
import functools as ft
from inspect import getdoc
import re

import h2o
from h2o.automl._base import H2OAutoMLBaseMixin
from h2o.automl._h2o_automl_output import H2OAutoMLOutput
from h2o.base import Keyed
from h2o.estimators import H2OEstimator
from h2o.exceptions import H2OResponseError, H2OValueError
from h2o.frame import H2OFrame
from h2o.job import H2OJob
from h2o.utils.shared_utils import check_id
from h2o.utils.typechecks import assert_is_type, is_type, numeric

class H2OInfoGram(H2OAutoMLBaseMixin, Keyed):
    def __init__(self,
                 model_id,
                 seed=None,
                 stopping_rounds=3,
                 stopping_metric="AUTO",
                 stopping_tolerance=None,
                 balance_classes=False,
                 max_runtime_secs=None,
                 infogram_algorithm,
                 infogram_algorithm_params,
                 model_algorithm,
                 model_algorithm_params,
                 sensitive_attributes,
                 conditional_info_threshold,
                 varimp_threshold,
                 data_fraction,
                 parallelism,
                 ntop,
                 pval,
                 **kwargs):
                 
        algo_parameters = None
        
