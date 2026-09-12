# GLIDENet

Gas-Liquid Interfacial Dynamics Ensemble Network.

GLIDENet is a community-driven benchmark dataset for gas-liquid two-phase CFD
and machine learning. The site is a static GitHub Pages catalogue: large data
files live on external platforms such as ModelScope, Kaggle, Zenodo, or trusted
institutional repositories, while this repository stores metadata, pages,
preview assets, and automation.

## Automation Model

The project keeps the proven intake and maintenance chain:

```text
Issue submission -> datasets/*.json -> draft PR -> maintainer review -> generated website
```

Updates and deletions are also data-driven:

```text
edit/delete datasets/*.json -> validation -> regenerate data and detail pages -> remove orphan pages
```

Generated files should not be edited directly.

## Site Pages

The public navigation follows the BlastNet-style distribution:

- Home
- Datasets
- Benchmarks
- Tutorials
- Contribute
- Events
- Cite
