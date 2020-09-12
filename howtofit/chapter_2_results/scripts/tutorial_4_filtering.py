# %%
"""
Tutorial 4: Filtering
=====================

In the previous tutorials, the _Aggregator_ has always loaded all of the results of all 3 fits.

However, suppose we had the results of other fits in the 'output' folder and we *only* wanted fits which used
a certain phase. Or, imagine we want the results of a fit to 1 specific data. In this tutorial, we'll learn how to use
the _Aggregator_'s filter tool, which filters the results and provides us with only the results we want.
"""

# %%
#%matplotlib inline

from autoconf import conf
import autofit as af
from howtofit.chapter_2_results import src as htf

import numpy as np
import os

workspace_path = os.environ["WORKSPACE"]
print("Workspace Path: ", workspace_path)

# %%
"""
Setup the configs and output folder for our non-linear search.
"""

# %%
conf.instance = conf.Config(
    config_path=f"{workspace_path}/howtofit/config",
    output_path=f"{workspace_path}/howtofit/output",
)

# %%
"""
When we load the aggregator, in this tutorial the output_path does not include the '/chapter2/aggregator' on the end, 
like it did in the previous tutorial. 

This means that, without filters, the _Aggregator_ will load all results in the output folder, including those from 
chapter 1 and the previous tutorials in this chapter.

We can first filter results to only include completed results. By including the *completed_only* input below, any 
results which are in the middle of a non-linear will be omitted and not loaded in the _Aggregator_.
"""

# %%
output_path = f"{workspace_path}/howtofit/output"

agg = af.Aggregator(directory=str(output_path), completed_only=True)

# %%
"""
First, lets print the number of _Samples_ objects the _Aggregator_ finds. Now we are pointing the _Aggregator_ to the
output folder, depending on what results are there this should find in excess of 3 sets of results, corresponding to
results from chapter 1 and tutorial 1 of chapter 2.
"""

# %%
print("Emcee Samples:\n")
print("Total Samples Objects = ", len(list(agg.values("samples"))), "\n")

# %%
"""
To remove the fits of previous tutorials and just keep the MCMCSamples of the 3 datasets fitted in this tutorial we can 
use the aggregator's filter tool. Below, we use the phase name of the results, 'phase_t2' which is unique to all 3 
fits, to filter our results are desired.
"""

# %%
phase_name = "phase_t2_agg"
agg_filter = agg.filter(agg.phase == phase_name)

# %%
"""
This filtered _Aggregator_ should now produce just 3 _Samples_ objects.
"""
print("Total Samples Objects = ", len(list(agg.values("samples"))), "\n")
samples_gen = agg_filter.values("samples")

# %%
"""
Alternatively, we can filter using strings, requiring that the string appears in the full path of the output
results. This is useful if you fit a large sample of data where:

 - Multiple results, corresponding to different phases and model-fits are stored in the same path.
 
 - Different runs using different _SettingsPhase_ are in the same path.
 
 - Fits using different non-linear searches, with different settings, are contained in the same path.

The example below shows us using the contains filter to get the results of the fit to only the first _Dataset_. 
"""

# %%
agg_filter_contains = agg.filter(
    agg.directory.contains("phase_t2_agg"), agg.directory.contains("gaussian_x1_0")
)
print("Directory Contains Filtered NestedSampler Samples: \n")
print(
    "Total Samples Objects = ", len(list(agg_filter_contains.values("samples"))), "\n\n"
)

# %%
"""
You can also filter by the type of non-linear search used, so that if you were to fit the same model to the same 
dataset with different non-linear searches you could load and compare their results.
"""

# %%
agg_filter_contains = agg.filter(agg.non_linear_search == "dynestystatic")
print("Directory Contains Filtered NestedSampler Samples: \n")
print(
    "Total Samples Objects = ", len(list(agg_filter_contains.values("samples"))), "\n\n"
)

# %%
"""
Filters can be combined to load precisely only the result that you want, below we use all the above filters to 
load only the results of the fit to the first lens in our sample.
"""
agg_filter_multiple = agg.filter(
    agg.phase == "phase_t2_agg", agg.directory.contains("gaussian_x1_0")
)
print("Multiple Filter NestedSampler Samples: \n")
print()
print(
    "Total Samples Objects = ", len(list(agg_filter_multiple.values("samples"))), "\n\n"
)