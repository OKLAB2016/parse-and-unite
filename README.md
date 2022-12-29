# Parse-and-unite
Parses, concludes and unites several Trans Proteomic Pipline (TPP) interact files and generates several Excel output files.

Parse-and-unite is a GUI-based software that combines and concludes several interact.pep.xml files into user-friendly xlsx files and Venn diagrams as well as calculation of ratio, standard deviation, and other parameters depending on the chosen mode. The merging process also include a filtration step based on false discovery rate and minimal number of matched ions.

#### NOTE:
This project includes modifications from this open-source code for Venn-diagrams : https://github.com/tctianchi/pyvenn


# 1.Prerequisites
You may need to import several packages to run this program (using pip install or downloading manually via links below)

   ###### 1. xlsxwriter:
      https://pypi.org/project/XlsxWriter/

   ###### 2. matplotlib:
      https://pypi.org/project/matplotlib/
      
      
# 2. Run
   The main file is xml_parser_view.py, you should run this file only.


# 3. Explanations and how-to
    

### Opening screen:
![image](https://user-images.githubusercontent.com/18205398/209855307-63dc16c4-7e8e-44de-a06b-753c6ae6b257.png)

Click the "Browse" button and select all your pep.xml samples files (note- if you choose more than 6 files, the script will not generate Venn diagrams for these samples)

Choose your output file name, this will be the name of your united file

Choose your error rate, as percentage. eptides with a probability lower than this FDR threshold will be excluded

Choose your running mode: 
## 1- Default: 

Quantify variable isotopic labelling difference.


## 2- Label free:

Quantify peptide's peak area based on label free.

## 3- K and uniform n-terms: 

Quantify variable isotopic labelling difference of a single amino acid while having fixed terminal modifications.

## 4- Variable:

Calculate variable modification occurrances.



When you all set, click the "Run" button.

##### On default mode you may see another window popping, asking you how to calculate your ratio (heavy/light or light/heavy)


![image](https://user-images.githubusercontent.com/18205398/209857437-dc7d157c-1833-432f-bac4-80b3a973c7ba.png)


### Output files:
When the program is finished, press "OK". Your source folder will open automatically and contain all your output files.


![image](https://user-images.githubusercontent.com/18205398/209857982-9b26c1fe-e862-4436-805f-5cfed2926202.png)



#### Venn PNGs
Four Venn diagrams- peptides intersections, protein intersections, PSM intersections and stripped intersections.

Example:


![image](https://user-images.githubusercontent.com/18205398/209858248-95246b08-7546-47c0-b800-240b235738ad.png)


#### Xlsx for each pep.xml file:
file-name_out.xlsx

These are the interim uniqe summary files for each output file.

   
 
#### OutPSM file:
   Informative table for PSM level features (unite all samples in a single file).
   
   
 #### United file:
   Informative table for peptide level features (unite all samples in a single file).
   
   
   
 ##### Ratio calculation and column descriptions:
   Peak area was calculated by quantifying and summing all the PSMs peak areas, in the case of isotopic labels
   the united file contains a "ratio" column, which is the  quotient of the light/ heavy areas.
   (modifications included in the peak area sum: oxidation (M), alkylation (C))
   



#### For any issue please contact me : glory.abr@gmail.com
