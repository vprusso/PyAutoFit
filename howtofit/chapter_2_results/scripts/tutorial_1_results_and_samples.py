# %%
"""
Tutorial 1: Results
===================

In this tutorial, we'll cover all of the output that comes from a _Phase_ in the form of a _Result_ object.

We'll use the same problem of fitting 1D profiles to noisy data, with the source code we use to do this in chapter 2
an adaption of the source code we completed chapter 1 using. It has new funtionality which we'll cover throughout this
chapter, but for this tutorial the source code is use as we used it before.

We used this object at various points in the previous chapter, and the bulk of material covered here is described in
the example script 'autofit_workspace/examples/simple/result.py'. Nevertheless, it is a good idea to refresh ourselves
about how results in **PyAutoFit** work before covering more advanced material.
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
Setup the configs as we did in the previous tutorial, as well as the output folder for our non-linear search.
"""

# %%
conf.instance = conf.Config(
    config_path=f"{workspace_path}/howtofit/config",
    output_path=f"{workspace_path}/howtofit/output/chapter_2",
)

# %%
"""
Now, lets create a _Dataset_ and fit it using a _Phase_, in an identical fashion to the previous chapter.
"""

# %%
from howtofit.simulators.chapter_2 import gaussian_x1

# %%
"""
When we fit the data-sets, we will omit the data-trimming demonstrated in the previous tutorial.
"""

# %%
settings_masked_dataset = htf.SettingsMaskedDataset(
    data_trim_left=None, data_trim_right=None
)

settings = htf.SettingsPhase(settings_masked_dataset=settings_masked_dataset)

# %%
"""The code below creates the _Dataset_ and mask as per usual."""

# %%
data = gaussian_x1.data
noise_map = gaussian_x1.noise_map
dataset = htf.Dataset(data=data, noise_map=noise_map)
mask = np.full(fill_value=False, shape=dataset.data.shape)

print(
    f"Emcee has begun running - checkout the "
    f"autofit_workspace/howtofit/chapter_2_results/output/phase_t1 folder for live "
    f"output of the results. This Jupyter notebook cell with progress once Emcee has completed - this could take a "
    f"few minutes!"
)

phase = htf.Phase(
    phase_name="phase_t1",
    profiles=af.CollectionPriorModel(gaussian=htf.profiles.Gaussian),
    settings=settings,
    search=af.DynestyStatic(),
)

"""Note that we pass the info to the phase when we run it, so that the aggregator can make it accessible."""
result = phase.run(dataset=dataset, mask=mask)


# %%
"""
__Result__

Here, we'll look in detail at what information is contained in the result.

It contains a *Samples* object, which contains information on the non-linear sampling, for example the parameters. 

The parameters are stored as a a list of lists, where:

 - The outer list is the size of the total number of samples.
 - The inner list is the size of the number of free parameters in the fit.

"""

# %%
samples = result.samples
print("All Parameters:")
print(samples.parameters)
print("Sample 10's third parameter value (Gaussian -> sigma)")
print(samples.parameters[9][1], "\n")

# %%
"""
The _Samples_ class also contains the log likelihood, log prior, log posterior and weights of every accepted sample, 
where:

 - The log likelihood is the value evaluated from the likelihood function (e.g. -0.5 * chi_squared + the noise 
 normalized).

 - The log prior encodes information on how the priors on the parameters maps the log likelihood value to the log
 posterior value.

 - The log posterior is log_likelihood + log_prior.

 - The weight gives information on how samples should be combined to estimate the posterior. The weight values 
 depend on the sampler used, for MCMC samples they are all 1 (e.g. all weighted equally).
"""

# %%
print("All Log Likelihoods:")
print(samples.log_likelihoods)
print("All Log Priors:")
print(samples.log_priors)
print("All Log Posteriors:")
print(samples.log_posteriors)
print("All Sample Weights:")
print(samples.weights, "\n")

# %%
"""
The samples contain many useful vectors, including the samples with the highest likelihood and posterior values:
"""

# %%
max_log_likelihood_vector = samples.max_log_likelihood_vector
max_log_posterior_vector = samples.max_log_posterior_vector

print("Maximum Log Likelihood Vector:")
print(max_log_likelihood_vector)
print("Maximum Log Posterior Vector:")
print(max_log_posterior_vector, "\n")

# %%
"""
This provides us with lists of all model parameters. However, this isn't that much use - which values correspond to 
which parameters?

The list of parameter names are available as a property of the  _Samples_ , as are parameter labels which can be used 
for labeling figures.
"""

# %%
print(samples.parameter_names)
print(samples.parameter_labels)
print("\n")

# %%
"""
It is more useful to return the _Result_'s as an instance, which is an instance of the model using the Python classes 
used to compose it.
"""

# %%
max_log_likelihood_instance = samples.max_log_likelihood_instance

# %%
"""
A model instance contains all the model components of our fit - which for the fit above was a single gaussian
profile (the word 'gaussian' comes from what we called it in the CollectionPriorModel when making the phase above).
"""

# %%
print(max_log_likelihood_instance.profiles.gaussian)

# %%
"""
We can unpack the parameters of the _Gaussian_ to reveal the maximum log likelihood parameters.
"""

# %%
print("Max Log Likelihood _Gaussian_ Instance:")
print("Centre = ", max_log_likelihood_instance.profiles.gaussian.centre)
print("Intensity = ", max_log_likelihood_instance.profiles.gaussian.intensity)
print("Sigma = ", max_log_likelihood_instance.profiles.gaussian.sigma, "\n")

# %%
"""
For our example problem of fitting a 1D _Gaussian_ profile, this makes it straight forward to plot the maximum
likelihood model:
"""

# %%
model_data = samples.max_log_likelihood_instance.profiles.gaussian.profile_from_xvalues(
    xvalues=np.arange(data.shape[0])
)

import matplotlib.pyplot as plt

plt.plot(range(data.shape[0]), data)
plt.plot(range(data.shape[0]), model_data)
plt.title("Illustrative model fit to 1D _Gaussian_ profile data.")
plt.xlabel("x values of profile")
plt.ylabel("Profile intensity")
plt.show()
plt.close()


# %%
"""
We can also access the 'median pdf' model, which is the model computed by marginalizing over the samples of every 
parameter in 1D and taking the median of this PDF.

The median pdf vector is readily available from the *Samples* object for you convenience.
"""

# %%
median_pdf_vector = samples.median_pdf_vector
print("Median PDF Vector:")
print(median_pdf_vector, "\n")

median_pdf_instance = samples.median_pdf_instance
print("Median PDF _Gaussian_ Instance:")
print("Centre = ", median_pdf_instance.profiles.gaussian.centre)
print("Intensity = ", median_pdf_instance.profiles.gaussian.intensity)
print("Sigma = ", median_pdf_instance.profiles.gaussian.sigma, "\n")


# %%
"""
The _Samples_ class also provides methods for computing the error estimates of all parameters at an input sigma 
confidence limit, which can be returned at the values of the parameters including their errors or the size of the 
errors on each parameter:
"""

# %%
vector_at_upper_sigma = samples.vector_at_upper_sigma(sigma=3.0)
vector_at_lower_sigma = samples.vector_at_lower_sigma(sigma=3.0)

print("Upper Parameter values w/ error (at 3.0 sigma confidence):")
print(vector_at_upper_sigma)
print("lower Parameter values w/ errors (at 3.0 sigma confidence):")
print(vector_at_lower_sigma, "\n")

error_vector_at_upper_sigma = samples.error_vector_at_upper_sigma(sigma=3.0)
error_vector_at_lower_sigma = samples.error_vector_at_lower_sigma(sigma=3.0)

print("Upper Error values (at 3.0 sigma confidence):")
print(error_vector_at_upper_sigma)
print("lower Error values (at 3.0 sigma confidence):")
print(error_vector_at_lower_sigma, "\n")

# %%
"""
All methods above are available as an instance:
"""

# %%
instance_at_upper_sigma = samples.instance_at_upper_sigma
instance_at_lower_sigma = samples.instance_at_lower_sigma
error_instance_at_upper_sigma = samples.error_instance_at_upper_sigma
error_instance_at_lower_sigma = samples.error_instance_at_lower_sigma

# %%
"""
An instance of any accepted sample can be created:
"""

# %%
instance = samples.instance_from_sample_index(sample_index=500)
print("Gaussian Instance of sample 5000:")
print("Centre = ", instance.profiles.gaussian.centre)
print("Intensity = ", instance.profiles.gaussian.intensity)
print("Sigma = ", instance.profiles.gaussian.sigma, "\n")

# %%
"""
Because _DynestyStatic_, a nested sampling *non-linear search* was used, the evidence of the model is also available 
which enables Bayesian model comparison to be performed.
"""

# %%
log_evidence = samples.log_evidence

# %%
"""
Finally, lets remind ourselves of the _Result_ class in the module:

 'chapter_2_results/src/phase/result.py' 
 
Here, we extended the _Result_ class with two additional methods:

 - max_log_likelihood_model_data
 - max_log_likelihood_fit
"""

# %%
htf.plot.Line.line(xvalues=dataset.xvalues, line=result.max_log_likelihood_model_data)
htf.plot.FitDataset.chi_squared_map(fit=result.max_log_likelihood_fit)

# %%
"""
The Probability Density Functions (PDF's) of the results can be plotted using the library:

 corner.py: https://corner.readthedocs.io/en/latest/

(In built visualization for PDF's and non-linear searches is a future feature of PyAutoFit, but for now you'll have to 
use the libraries yourself!).
"""

import corner

corner.corner(xs=samples.parameters, weights=samples.weights)