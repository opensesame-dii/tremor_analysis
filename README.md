# dependancies
- uv (as python package manager)

# installation
```
git clone git@github.com:opensesame-dii/tremor_analysis.git
cd tremor_analysis
uv sync
```

# launch
```
uv run trun
```

# file location

Proper file location and directory structure is required for this system to work correctly.

- All data files to be analyzed should be placed within a single target directory.
- Each participant's or measurement data should be organized in separate subdirectories within the target directory.
- Each subdirectory should contain 1 or 2 CSV file(s) with the data to be analyzed.
- The CSV files intended for analysis should not have the extension ".tremor.csv". Files with this extension will be excluded from analysis.

Here are an example.
```
target_dir/
├── measurement_01/
│   ├── right_hand.csv
│   └── left_hand.csv
├── measurement_02/
│   ├── right_hand.csv
│   └── left_hand.csv
├── measurement_03/
│   └── measurement.csv
```

# how to use

1. launch the system using the command above.
1. In the GUI, specify the target directory containing the data files.
1. Configure any additional settings as needed. Configuration is saved into "~/.tremor_analysis_config.yaml".
1. Preview the list of files to be analyzed by clicking the "Preview Files" button if you need.
1. Start the analysis by clicking the "Run" button.
1. After the analysis is complete, the results will be saved in `target_directory/result_1file.tremor.csv`, `target_directory/result_2file.tremor.csv` and `target_directory/result_images`. `target_directory` is opened by clicking the "Open Result" button.

For encoding settings, you can view the list of available encodings:
```python
import encodings
import pkgutil
encs = sorted(m.name for m in pkgutil.iter_modules(encodings.__path__))
print(len(encs))
print(encs)
```

# example
`example_directory_structure` contains an example directory structure with sample data files for testing the system. You can use it to verify that the system is functioning correctly.
In this example, `example_directory_structure/target_dir` should be specified as the target directory by clicking "Select Folder" button in the GUI.

`generate_sample_file.py` and `run_generate_sample.sh` are scripts to generate sample data files.

# how to add new analysis method
All python classes for analysis are implemented in `tremor_analysis/analysis_methods/`.
If you want to implement additional analysis, follow the example of `tremor_analysis/analysis_methods/spectrogram.py` by inheriting from class `tremor_analysis.analysis_methods.base.AnalysisMethodBase` and implement the following items:
- The class variable `ACCEPTABLE_DATA_COUNT`
- Configuration items via the `config` class variable
- Analysis processing via implementation of the `run()` method
