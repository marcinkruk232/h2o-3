import sys
sys.path.insert(1,"../../")
import h2o
import tempfile
from h2o.estimators import H2OGradientBoostingEstimator, H2OGenericEstimator
from tests import pyunit_utils

# Test of MOJO convenience methods
def generic_blank_constructor():
    from h2o.estimators import H2ORandomForestEstimator

    h2o_df = h2o.import_file("/Users/mkurka/git/h2o/h2o-3/private/datasets/BNPParibas.csv")

    predictors = h2o_df.columns
    response = "v58"
    predictors.remove(response)

    cars_drf = H2ORandomForestEstimator(
        ntrees=1,
        max_depth=10,
        min_rows=1,
        nbins=4096,
        nbins_top_level=4096,
        min_split_improvement=1e-06,
        seed=3
    )
    cars_drf.train(x=predictors,
                   y=response,
                   training_frame=h2o_df,
                   )

    from h2o.tree import H2OTree

    print(cars_drf.predict(h2o_df))
    node_assignments_num = cars_drf.predict_leaf_node_assignment(h2o_df, type="Node_ID")

    mojo_path = cars_drf.download_mojo("prcak")
    print(h2o.print_mojo(mojo_path, format="json"))
    tree = H2OTree(model=cars_drf, tree_number=0)
    children = []
    for i in range(0, len(tree)):
        if (tree.left_children[i] == -1):
            children.append(tree.node_ids[i])

    print(len(node_assignments_num.unique()))
    print(len(children))
     
    xx = set(node_assignments_num.as_data_frame()["T1"])
    print(set(children) - xx)
    
    assert len(node_assignments_num.unique()) == len(children)


if __name__ == "__main__":
    pyunit_utils.standalone_test(generic_blank_constructor)
else:
    generic_blank_constructor()
