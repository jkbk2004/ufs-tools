# hpc-usage-visual-metrics
### Python script for visualizing HPC resources
- Example of running, passing in sample log data, and exporting graphs to data directory:
```
python ./hpcUsageVisualizer.py -f ./sampleData/ -o ./data/
```
- Providing an output location argument will skip the graph popups.
- Figures for core hour allocation, usage, and fair share will be saved.
