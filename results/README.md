``results/`` contains the quantiles extracted from a sample of documents, a pdf produced by ``filter_analysis.ipynb`` and results for filter runtime on 32 CPUs.

There are two versions, one with 10th, 25th, 75th and 90th quantiles, and one with 10th, 20th, ..., 90th quantiles.
Use ``parse_quantiles.py`` to parse these files into the _rule file_, which is needed in ``filter.py``.
