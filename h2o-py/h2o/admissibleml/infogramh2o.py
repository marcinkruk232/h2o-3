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
from h2o.h2o import _check_connection
from h2o.job import H2OJob
from h2o.utils.metaclass import h2o_meta
from h2o.utils.shared_utils import check_id
from h2o.utils.typechecks import assert_is_type, is_type, numeric

class H2OInfoGram(H2OEstimator, h2o_meta(Keyed)):
    def __init__(self,
                 model_id=None,
                 seed=None,
                 max_runtime_secs=None,
                 infogram_algorithm=None,
                 infogram_algorithm_params=None,
                 model_algorithm=None,
                 sensitive_attributes=None,
                 conditional_info_threshold=0.1,
                 varimp_threshold=0.1,
                 data_fraction=1.0,
                 parallelism=None,
                 ntop=50,
                 pval=False, # may need to add more here
                 **kwargs):
        super(H2OInfoGram, self).__init__()
        # Check if H2O jar contains AdmissibleML
        try:
            h2o.api("GET /3/Metadata/schemas/InfoGramV99")
        except h2o.exceptions.H2OResponseError as e:
            print(e)
            print("*******************************************************************\n" \
                  "*Please verify that your H2O jar has the proper AdmissibleML extensions.*\n" \
                  "*******************************************************************\n" \
                  "\nVerbose Error Message:")
        # check for valid parameter settings    
        assert_is_type(model_id, None, str)
        assert_is_type(max_runtime_secs, None, int)
        assert_is_type(seed, None, int)
        assert_is_type(infogram_algorithm, None, str)
        assert_is_type(infogram_algorithm_params, None, dict)
        assert_is_type(model_algorithm, None, str)
        assert_is_type(sensitive_attributes, None, tuple)
        if isinstance(sensitive_attributes):
            for obj in sensitive_attributes:
                assert_is_type(obj, str)
        assert_is_type(conditional_info_threshold, numeric)
        assert conditional_info_threshold >= 0 and conditional_info_threshold <= 1, "conditional_info_threshold should be between 0 and 1."
        assert_is_type(varimp_threshold, numeric)
        assert varimp_threshold >= 0 and varimp_threshold <= 1, "varimp_threshold should be between 0 and 1."
        assert_is_type(data_fraction, numeric)
        assert data_fraction > 0 and data_fraction <= 1, "data_fraction should exceed 0 and <= 1."  
        assert_is_type(parallelism, None, int)
        assert_is_type(ntop, int)
        assert_is_type(pval, bool)
        model_algorithm_params = {}
        infogram_algorithm_params = {}
        for k in kwargs:
            if (k == 'model_algorithm_params'):
                model_algorithm_params = kwargs[k] or {}
            elif (k == 'infogram_algorithm_params'):
                infogram_algorithm_params = kwargs[k] or {}
            else:
                raise TypeError("H2OInfoGram got an unexpected keyword argument '%s' % k")
        # set parameters
        self._parms = {}
        self._job = None  # used when _future is True#
        self.model_id = model_id
        self.max_runtime_secs = max_runtime_secs
        self.seed = seed
        self.infogram_algorithm = infogram_algorithm
        self.infogram_algorithm_params = infogram_algorithm_params
        self.model_algorithm = model_algorithm
        self.model_algorithm_params = model_algorithm_params
        self.sensitive_attributes = sensitive_attributes
        self.conditional_info_threshold = conditional_info_threshold
        self.varimp_threshold = varimp_threshold
        self.data_fraction = data_fraction
        self.parallelism = parallelism
        self.ntop = ntop
        self.pval = pval
        self._parms["_rest_version"] = 99
    
    # copy from automl
    def train(self, x=None, y=None, training_frame=None, verbose=False, offset_column=None, weights_column=None,
              ignored_columns=None):
        has_training_frame = training_frame is not None or self.training_frame is not None
        if not(has_training_frame):
            raise H2OValueError('Training frame is absent.')
        
        parms = self._parms.copy()
        parms["training_frame"] = training_frame
        self.training_frame = training_frame
        ncols = self.training_frame.ncols
        names = self.training_frame.names
        ignored_columns_set = self.training_frame.names
        if (ignored_columns is None):
            ignored_columns = set()

        if y is None and self.response_column is None:
            raise H2OValueError('The response column (y) is not set; please set it to the name of the column that you are trying to predict in your data.')
        elif y is not None:
            self.response_column = self.assertValidCol(y, ncols, names)
            parms["response_column"] = self.response_column
            ignored_columns_set.remove(parms["response_column"])

        if x is not None:
            assert_is_type(x, list)
            xset = set()
            for xi in x:
                xname = self.assertValidCol(xi, ncols, names)
                if xname in ignored_columns:
                    raise H2OValueError("Predictor x and ignored_columns cannot be specified simultaneously")
                xset.add(xname)
                ignored_columns_set.remove(self.assertValidCol(xi, ncols, names))
        if offset_column is not None:
            parms["offset_column"] = self.assertValidCol(offset_column, ncols, names)
            ignored_columns_set.remove(parms["offset_column"])
        if weights_column is not None:
            parms["weights_column"] = self.assertValidCol(weights_column, ncols, names)
            ignored_columns_set.remove(parms["weights_column"])
        ignored_columns_set.remove(ignored_columns)
        parms['ignored_columns'] = ignored_columns_set

        resp = self._build_resp = h2o.api('POST /99/InfogramBuilder', json=parms)
        if 'job' not in resp:
            raise H2OResponseError("Backend failed to build the InfoGram job: {}".format(resp))
        

    def assertValidCol(self, x, ncols, colNames):
        if is_type(x, int):
            if not (0 <= x < ncols):
                raise H2OValueError("Column %d does not exist in the training frame" % x)
            return colNames[x]
        if is_type(x, str):
            if x not in colNames:
                raise H2OValueError("Column %s not in the training frame" % x)
            return x
    
    @property
    def key(self):
        return self._id
