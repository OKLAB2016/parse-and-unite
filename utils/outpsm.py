import xlsxwriter
import os
import re
PROTON = 1.00727646688

class OutPSM:
    """
    fields for outPSM.xlsx
    a little duplication for peptide class but repetition needed
    """
    def __init__(self, seq, start, end, prot, alternative, prob, expect, matched_ions,tot_ions,
                 assumed, neutral_mass, calc_neu, ppm, file, k_heavy, k_light, modif, n_heavy, n_light,
                 k_h_int, k_l_int, n_h_int, n_l_int, m, c, m_float, c_float, fixed, running_mode, ntt, retention):
        self.peptide: str = seq                   # attrib "peptide" of "search_hit" in xml
        self.start: str = start               # attrib "peptide_prev_aa"  of "search_hit" in xml
        self.end: str = end                   # attrib "pepide_next_aa"  of "search_hit" in xml
        self.modified: str = modif          # TODO should call modified function with start and end for form the right template
        self.prot: str = prot                 # attrib "protein" of "search_hit" in xml
        self.alternative: list = alternative  # all allternative_protein.attrib(protein)
        self.prob: float = prob               # attrib  "probabilty" of "search_hit\ peptideprophet_result" in xml
        self.expect: float = expect               # attrib "expect value"
        self.num_matched_ions: int = matched_ions                 # number of matched ions
        self.total_ions : int = tot_ions            #tot_num_ions
        self.assumed_charge = assumed   #assumed_charge
        self.precursor_neutral_mass = neutral_mass  #precursor_neutral_mass
        self.calc_neutral_pep_mass = calc_neu   #calc_neutral_pep_mass
        self.ppm = ppm  # guess it is mass diff
        self.sample_name = file
        self.k_heavy = k_heavy
        self.k_light = k_light
        self.n_heavy = n_heavy
        self.n_light = n_light
        self.m_mass = m
        self.m_mass_outPSM = m_float
        self.c_mass = c
        self.c_mass_outPSM = c_float
        self.c_is_fixed = fixed
        self.ion_template = ""
        self.modified_template(k_h_int, k_l_int, n_h_int, n_l_int)
        self.type = running_mode
        self.ntt = ntt # num_tol_term
        self.retention = retention #retention time
        self.mz_ratio_theoretical = (self.calc_neutral_pep_mass + (self.assumed_charge * PROTON))/self.assumed_charge
        self.mz_ratio_experimental = (self.precursor_neutral_mass + (self.assumed_charge * PROTON))/self.assumed_charge


    def modified_template(self, k_h, k_l, n_h, n_l):
        if self.c_is_fixed:
            self.modified = self.modified.replace('C', 'C[' +str(self.c_mass_outPSM) + ']')
        else:
            self.modified = self.modified.replace(str(self.c_mass), str(self.c_mass_outPSM))
        self.modified = re.sub('K([^\[])', "K[" + str(self.k_light) + "]" + r"\1", self.modified)
        self.modified = self.start + '.' + self.modified + "." + self.end
        self.modified = self.modified.replace("n[" +str(n_l)+ "]", "n[" +str(self.n_light) + "]")
        self.modified = self.modified.replace(str(k_h), str(self.k_heavy))
        self.modified = self.modified.replace(str(n_h), str(self.n_heavy))
        self.modified = self.modified.replace(str(self.m_mass), str(self.m_mass_outPSM))
        self.ion_template = str(self.num_matched_ions) + "|" + str(self.total_ions)
        base = os.path.basename(self.sample_name)  # remove path name
        base = os.path.splitext(base)  # remove .xmk
        base = base[0]  # take only the name. no need of .xml
        if base.startswith('interact-'):  # if the filename start with "interact-" then remove it
            base = re.sub('interact-', '', base)
        if base.endswith('.pep'):  # if filename end with "."pep" remove it
            base = re.sub('\.pep$', '', base)
        self.sample_name = base

    def class_to_list(self):
        pep = []
        pep.append(self.peptide)
        pep.append(self.modified)
        pep.append(self.prot)
        pep.append("".join(self.alternative))
        pep.append(self.prob)
        pep.append(self.expect)
        pep.append(self.ion_template)
        pep.append(self.assumed_charge)
        pep.append(self.precursor_neutral_mass)
        pep.append(self.calc_neutral_pep_mass)
        pep.append(self.ppm)
        pep.append(self.ntt)
        pep.append(self.retention)
        pep.append(self.mz_ratio_theoretical)
        pep.append(self.mz_ratio_experimental)
        pep.append(self.sample_name) # importent - last element in list! keep it that way
        return pep


def xlsx_outpsm( list_out_psm, out, file):


            """"
            export the data to excel sheet
            """
            sheets_dict = dict()
            for pep in list_out_psm:
                ll = pep.class_to_list()
                if ll[-1] in sheets_dict.keys():
                    sample_name = ll[-1]
                    ll.pop()
                    sheets_dict[sample_name].append(ll)
                else:
                    sample_name = ll[-1]
                    ll.pop()
                    sheets_dict[sample_name] = list()
                    sheets_dict[sample_name].append(ll)


            workbook = xlsxwriter.Workbook(os.path.dirname(file) +'/outPSM_' + str(out) + '.xlsx')

            for sample_name in sheets_dict.keys():
                sheet = workbook.add_worksheet(sample_name)
                headers = ['Peptide', 'Modified peptide', 'Protein', 'Alternative proteins', 'Probability', 'Expect',
                       'Ions', 'Assumed charge', 'Precursor neutral mass', 'Calc neutral pep mass', 'PPM', 'NTT', 'retention time', 'm/z ratio theoretical', 'm/z ratio experimental']
                headers_len = len(headers)
                for x in range(headers_len):
                    sheet.write(0, x, headers[x])
                # col and raw are just for the for iterations below
                row = 1
                for y in range(len(sheets_dict[sample_name])):
                    for x in range(headers_len):
                        sheet.write(row, x, sheets_dict[sample_name][y][x])
                    row += 1
            workbook.close()  # creating the output.xlsx

