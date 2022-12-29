# parse-and-unite
Parse, conclude and unite several Trans Proteomic Pipline (TPP) intetact files while generating sevral Excel output files.

parse-and-unite is a GUI-based software that combines and concludes several interact.pep.xml samples into user-friendly xlsx files and venn diagramms as well as calculation of ratio, st deviation, and other parameters depending on the chosen mode.

#### NOTE:
This project include modifications from this open-source code for venn-diagrams : https://github.com/tctianchi/pyvenn


##### for any issue please contact me : glory.abr@gmail.com 

# 1.Prerequisites
You may need to import several packages in order to run this program (using pip install or downloading manually via links below)

   ###### 1. xlsxwriter:
      https://pypi.org/project/XlsxWriter/

   ###### 2. matplotlib:
      https://pypi.org/project/matplotlib/
      
      
# 2. Run
   The main file is xml_parser_view.py, you should run it only.


# 3. Explenations and how-to
    

### Opening screen:
![image](https://user-images.githubusercontent.com/18205398/209855307-63dc16c4-7e8e-44de-a06b-753c6ae6b257.png)

Click the "Browse" button and select all your pep.xml samples files (note- if you choose more than 6 files, the script will not generate venn diagrams for these samples)

Choose your output file name, this will be the name for the united file

Choose your error rate, this rate is in percentage. peptides lower than this thrashhold will be excluded

Choose your running mode: 
1- default : quantify variable isotopic labeling difference
2- label free: quantify peptide's pick area based on label free
3- K and uniform n-terms: quantify variable isotopic labeling difference of single amino acid while having fixed terminal modifications
4- variable: calculate variable modification occurances 

Then click the "Run" button.

###### On default mode you may see another window popping, asking you how to calculate your ratio (heavy/light or light/heavy)

![image](https://user-images.githubusercontent.com/18205398/209857437-dc7d157c-1833-432f-bac4-80b3a973c7ba.png)


### Output files:
When the program will be finished, press "OK". your source folder will be opened automaticlly with all your output files.


![image](https://user-images.githubusercontent.com/18205398/209857982-9b26c1fe-e862-4436-805f-5cfed2926202.png)



#### Venn PNGs
You should get four venn diagramms- peptides intersections, protein intersections, PSM intersections and stripped intersections.

Example:


![image](https://user-images.githubusercontent.com/18205398/209858248-95246b08-7546-47c0-b800-240b235738ad.png)


#### xlsx for each pep.xml file:
<file-name>_out.xlsx
these are the uniqe summery for each file individually


   
 
#### outPSM file:
   informative table for psm level features (unite all samples in a single file)
   
   
 #### united file:
   informative table for peptive level features (unite all samples in a single file)
   
   
   
 #####ratio calculation and column explentations:
   peak area was callculated by quantifying and summing all the PSMs peak areas, in case of isotopic labels
   the united file contains "ratio" column, which the divition product of the light/ heavy areas.
   (modifications included in the peak are sum: oxidation (M) , alkylation (C))
   
