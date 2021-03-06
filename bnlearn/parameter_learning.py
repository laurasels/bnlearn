"""Techniques for parameter learning.

Description
-----------
Parameter learning is the task to estimate the values of the conditional probability distributions (CPDs).
To make sense of the given data, we can start by counting how often each state of the variable occurs.
If the variable is dependent on the parents, the counts are done conditionally on the parents states,
i.e. for seperately for each parent configuration

Currently, the library supports parameter learning for *discrete* nodes:
    * Maximum Likelihood Estimation
    * Bayesian Estimation
"""
# ------------------------------------
# Name        : parameter_learning.py
# Author      : E.Taskesen
# Contact     : erdogant@gmail.com
# Licence     : See licences
# ------------------------------------


# %% Libraries
from pgmpy.estimators import MaximumLikelihoodEstimator, BayesianEstimator  # ParameterEstimator


# %% Sampling from model
def fit(model, df, methodtype='bayes', verbose=3):
    """Learn the parameters given the DAG and data.

    Parameters
    ----------
    model : dict
        Contains key model and adjmat (adjacency matrix).
    df : pd.DataFrame()
        Pandas DataFrame containing the data.
    methodtype : str, optional
        strategy for parameter learning.. The default is 'bayes'.
        'ml' or 'maximumlikelihood' (default) :Learning CPDs using Maximum Likelihood Estimators
        'bayes' :Bayesian Parameter Estimation
    verbose : int, optional
        Print progress to screen. The default is 3.
        0: NONE
        1: ERROR
        2: WARNING
        3: INFO (default)
        4: DEBUG
        5: TRACE


    Returns
    -------
    dict with model.


    Examples
    --------
    >>> df = bnlearn.import_example()
    >>> model = bnlearn.import_DAG('sprinkler', CPD=False)
    >>> model_update = bnlearn.parameter_learning.fit(model, df)
    >>> bnlearn.plot(model_update)
    >>>
    >>> # LOAD BIF FILE
    >>> model = bnlearn.import_DAG('alarm')
    >>> df = bnlearn.sampling(model, n=1000)
    >>> model_update = bnlearn.parameter_learning.fit(model, df)
    >>> G = bnlearn.plot(model_update)

    """
    config = dict()
    config['verbose'] = verbose
    config['method'] = methodtype
    adjmat = model['adjmat']

    if isinstance(model, dict):
        model = model['model']
    if verbose>=3: print('[BNLEARN][PARAMETER LEARNING] Computing parameters using [%s]' %(config['method']))

#    pe = ParameterEstimator(model, df)
#    print("\n", pe.state_counts('Cloudy'))
#    print("\n", pe.state_counts('Sprinkler'))

    """
    Maximum Likelihood Estimation
        A natural estimate for the CPDs is to simply use the *relative frequencies*,
        with which the variable states have occured. We observed x cloudy` among a total of `all clouds`,
        so we might guess that about `50%` of `cloudy` are `sprinkler or so.
        According to MLE, we should fill the CPDs in such a way, that $P(\text{data}|\text{model})$ is maximal.
        This is achieved when using the *relative frequencies*.

    While very straightforward, the ML estimator has the problem of *overfitting* to the data.
    If the observed data is not representative for the underlying distribution, ML estimations will be extremly far off.
    When estimating parameters for Bayesian networks, lack of data is a frequent problem.
    Even if the total sample size is very large, the fact that state counts are done conditionally
    for each parents configuration causes immense fragmentation.
    If a variable has 3 parents that can each take 10 states, then state counts will
    be done seperately for `10^3 = 1000` parents configurations.
    This makes MLE very fragile and unstable for learning Bayesian Network parameters.
    A way to mitigate MLE's overfitting is *Bayesian Parameter Estimation*.
    """

    # Learning CPDs using Maximum Likelihood Estimators
    if config['method']=='ml' or config['method']=='maximumlikelihood':
        mle = MaximumLikelihoodEstimator(model, df)
        for node in mle.state_names:
            print(mle.estimate_cpd(node))

    """
    Bayesian Parameter Estimation
        The Bayesian Parameter Estimator starts with already existing prior CPDs,
        that express our beliefs about the variables *before* the data was observed.
        Those "priors" are then updated, using the state counts from the observed data.

    One can think of the priors as consisting in *pseudo state counts*, that are added
    to the actual counts before normalization. Unless one wants to encode specific beliefs
    about the distributions of the variables, one commonly chooses uniform priors,
    i.e. ones that deem all states equiprobable.

    A very simple prior is the so-called *K2* prior, which simply adds `1` to the count of every single state.
    A somewhat more sensible choice of prior is *BDeu* (Bayesian Dirichlet equivalent uniform prior).
    For BDeu we need to specify an *equivalent sample size* `N` and then the pseudo-counts are
    the equivalent of having observed `N` uniform samples of each variable (and each parent configuration).
    """
    if config['method']=='bayes':
        model.fit(df, estimator=BayesianEstimator, prior_type="BDeu", equivalent_sample_size=1000)  # default equivalent_sample_size=5

        for cpd in model.get_cpds():
            if verbose>=3: print("CPD of {variable}:".format(variable=cpd.variable))
            if verbose>=3: print(cpd)
    
    out = {}
    out['model'] = model
    out['adjmat'] = adjmat

    return(out)
