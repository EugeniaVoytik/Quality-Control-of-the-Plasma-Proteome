# Quality-Control-of-the-Plasma-Proteome Platform [![DOI](https://zenodo.org/badge/162268441.svg)](https://zenodo.org/badge/latestdoi/162268441)
(The copyright holder for this preprint https://doi.org/10.15252/emmm.201910427)

This platform is developed to help clinical researches
- to determine the overall quality of each sample in a clinical study
- to assess the quality of the whole study in terms of potential systematic biases
- to evaluate individual, significantly altered proteins in case-control comparisons

The website is available at http://plasmaproteomeprofiling.com/.

---
## Workflow
The principle operation for the “Quality Control of the Plasma Proteome” online platform in Plasma Proteome Profiling is illustrated in the following scheme:

![Computational Quality Control of the Plasma Proteome workflow](Images/workflow.png)

Before entering the platform, MS data are analyzed by MaxQuant or similar software packages. The resulting file, an annotated list of protein intensities (‘proteinGroups.txt’), is uploaded on the web page **_(A)_**. Upon successful verification **_(B)_** and comparison to a list of contamination markers **_(C)_**, a data structure is built in Python using a list of built-in Python libraries (NumPy, Pandas, SciPy, Scikit-learn) **_(D)_**. Through the user-friendly web interface **_(E)_**, graphically illustrated results for the quality assessments of proteomics data are presented online on the web page **_(F)_**.

---
## User Guide

### Load the data
To start working with the tool, the user needs to:
- Upload own "proteinGroups.txt" file, and then specify the Control (*obligatory) and Sample (*optional) identifiers. Download [attached file](https://github.com/MannLabs/Quality-Control-of-the-Plasma-Proteome/blob/master/data/proteinGroups_Sepsis_log.txt) as an example. Use "healthy" as the "Identifier for Control Group". Click the "Submit" button.
- Press the "Example" button to upload the example file - `proteinGroups_Weight_loss_study.txt`.
If you use the website version, take into account the response time (~ 30 sec to build all plots and the GUI). Therefore, it's recommended to deploy and use the tool locally.

### "Individual sample quality" panel
To separately assess the individual sample quality with respect to the contamination ratio of each of the three quality marker panels, use "Platelets", "Erythrocytes" and "Coagulation" panels. Samples annotated with their names have poor quality as assessed by the default cut-off value (dashed red line) of three standard deviations from the average contamination ratios. An interactive slider allows changing the threshold value. Hovering with the cursor over the values in the graph allows checking the calculated value and the name of the sample. . For the loaded file, this information can be saved by clicking "Download Calculated Data" after the "Coagulation" panel.

###	"Systemic bias" panel
To analyze the dataset for systematic bias and to illustrate the significance and the fold change of a comparison of case and control study groups, use the "Systemic bias" panel. In general, a volcano plot is a graphical method for visualizing changes in replicate data, where proteins that are highly dysregulated are farther to the left and right on the y-axis, while highly significant fold changes appear higher on the x-axis of the plot. The Log10 T-test difference (fold change) in the proteins levels is depicted on the x-axis and the –log10 p-value on the y-axis. Proteins above a cut-off (dashed red line) are considered to be significantly different between two analyzed groups (p<0.05).  Proteins in each of the three quality marker panels can be turned on and off by clicking on their name in the legend. Hovering with the cursor over the proteins in the volcano plot allows the user to get information about x- and y-values of the protein and its name. Clicking on the protein, it will be displayed in the global correlation map. This allows checking whether the protein falls close to any of the quality marker clusters.
In the "Systemic bias" panel the volcano plot is visualized shown the control group vs. sample.

###	"Evaluation of potential markers" panel
To correlate all proteins with at least 50% valid values and cluster them hierarchically, where the proteins of the same origin or with the same regulation mechanism are clustered together. The heatmap is constructed with a standard algorithm in SciPy and Scikit-learn algorithm as explained in a later section. Red patches in the global correlation map indicate positive and blue patches negative Pearson correlations. The top three proteins of each marker panel will be also automatically highlighted with arrows in the heatmap, which have the same color as the corresponding marker panel in the volcano plot. After clicking on the protein in the volcano plot, it will be shown on the heat map.

---
## Deployment (python3)
```
* git clone https://github.com/EugeniaVoytik/Quality-Control-of-the-Plasma-Proteome.git
* cd Quality-Control-of-the-Plasma-Proteome
* virtualenv -p python3 env
* source env/bin/activate
* pip install -r requirements.txt
* python run.py
```

---
## Authors
All authors and contributors are mentioned in the article(https://doi.org/10.15252/emmm.201910427).

---
## License

AlphaViz was developed by the [Mann Labs at the Max Planck Institute of Biochemistry](https://www.biochem.mpg.de/mann) and is freely available with an [Apache License](LICENSE.txt).
