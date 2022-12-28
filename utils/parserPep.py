from utils.peptide import Peptide
from utils.outpsm import OutPSM, xlsx_outpsm
import re
import os
from xml.etree import ElementTree
MIN_MATCHED_IONS = 5

class ParserPep:

    def __init__(self, input, mode, out):
        self.out_file_name = out
        self.list_outPSM = list()
        self.file_name = input
        #self.output_file_name = output
        self.dict_peptides = {}
        self.pep_modification_set = set()
        self.namespace = ""
        self.root = ""
        self._init_root_and_namespace()
        self.c = 0
        self.running_mode = mode
        self.psm = 0  # how many peptides (passed error rate) found in file
        self.peptide_modification_counter = 0   # how many modifications of all pep found in file (passed error rate)
        self.stripped_pep = 0    # how many different seq(ignoring modification) found in file(passed error rate)
        self.psm_list = list()   # all pep modification in including repetitions, this is for venn psm diagram
        #self.modifications_in_file = list()     # list of dict! amino / value / counter all / counter mod
                                                # for table2 - sum all modifications in files.
                                                # counter all = how many times the amino acid appeard in file
                                                # counter mod = how many appered in file with the value modification
        self.lysine_heavy_mass = 0       # changed by func "_update_n_and_k_mass", called from parser dict
        self.lysine_light_mass = 0
        self.lysine_light_mass_outPSM = 0
        self.lysine_heavy_mass_outPSM = 0
        self.n_heavy_mass = 0
        self.n_light_mass = 0
        self.n_light_mass_outPSM = 0
        self.n_heavy_mass_outPSM = 0
        self.m_mass = 0
        self.m_mass_outPSM = 0
        self.c_mass = 0
        self.c_mass_outPSM = 0
        self.c_is_fixed = 1     # 1 = N , 0= Y in _update_k_and_m_masses
        self.protein_set = set()        # will contain all attrib "protein" of hits in xml file



    def update_psm_pep_and_stripped(self):
        """
        self.psm (peptide_counter)
        self.peptide_modification_counter
        self.stripped_pep
        for each of the files

        those will be latter put in an xlsx table file
        :return:
        """
        self.stripped_pep = len(self.dict_peptides)
        #print(self.stripped_pep)
        for seq in self.dict_peptides.values():
            self.psm += seq.counter
        self.peptide_modification_counter = len(self.pep_modification_set)
        #print(self.pep_modification_set)
        #os._exit(5)
        #print(self.psm)
        #exit(1)


    # there is a namespace before root, it is pain in the ass
    # so this function cut it so other functions in ElementTree would work properly
    def _namespace(self, element):
        m = re.match(r'\{.*\}', element.tag)
        return m.group(0) if m else ''

    # def k_count(self, seq: str):
    #     """
    #     how many lysines(unmarked+heavy) in peptide
    #     """
    #     return seq.count("K")
    # def k_heavy_count(self, seq: str, counter_all):
    #     """
    #     how many heavy lysines (marked K[162]) in peptide
    #     param "counter_all" is the return value of k_count - just for assertion
    #     """
    #     temp = seq.count("K[162]")
    #     assert (temp >= counter_all)
    #     return temp

    def little_test(self, mod: str):
        assert (mod.count("[43]") == 1)

    def _k_peptide_type(self, seq, n_uniform=0):
        """
        if the peptide has no lysines(K) in it - return "no k"
        if the peptide is heavy == all lysines are [162] - return "heavy"
        id the peptide is light == all lysines are unmarked - return "light"
        if the peptide is mixed (heavy&light) - return "bad kitty"
        """
        k_all = seq.count("K")
        if self.lysine_heavy_mass == 0:
            return "no k"
        re_ = "K[" + str(self.lysine_heavy_mass) + "]"
        k_heavy = seq.count(re_)
        k_light = k_all - k_heavy
        if k_all == 0:
            # no lysines in pep
            return "no k"
        elif k_heavy == k_all:
            assert (k_all > 0)
            assert (k_light == 0)
            if (not n_uniform) and str(seq).startswith("n[" + str(self.n_light_mass)):
                return "bad kitty"
            else:
                return "heavy"
        elif k_light == k_all:
            assert (k_all > 0)
            assert (k_heavy == 0)
            if (not n_uniform) and str(seq).startswith("n[" + str(self.n_heavy_mass)):
                return "bad kitty"
            else:
                return "light"
        else:
            assert (k_all > 0)
            return "bad kitty"


    # check if there is modification in the n term
    # start with "n[29 |15|18 | 35] then the seq of peptide
    def _modification_n(self, seq, mod):
        assert self.n_light_mass   #if one of them is "0" then it is wrong mode
        assert self.n_heavy_mass
        re_heavy = "n[" + str(self.n_heavy_mass) + "]"
        re_light = "n[" + str(self.n_light_mass) + "]"
        if mod.startswith(re_heavy):
            self.dict_peptides[seq].add_n_heavy()
        elif mod.startswith(re_light):
            self.dict_peptides[seq].add_n_light()


    # error rate is the minimum probability we want
    # if peptide has probability < error_rate we pass it
    def _calc_error_rate(self, err):
        error = self.root.findall('.//' + self.namespace + 'roc_error_data')
        # if we  do not find the filed charge =all we return -1
        error_rate = -1
        for x in error:
            if x.attrib['charge'] == "all":
                error_point = x.findall('.//' + self.namespace + 'error_point')
                for y in error_point:

                    if y.attrib['error'] == str(err):
                        error_rate = y.attrib['min_prob']
                        error_rate = float(error_rate)
                        break
                    else:
                        continue
                else:
                    continue
        #print(error_rate)
        return error_rate

    def _init_root_and_namespace(self):
        full_file = os.path.abspath(self.file_name)
        dom = ElementTree.parse(full_file)
        self.root = dom.getroot()
        self.namespace = self._namespace(self.root)


    def _expect_calc(self, x):
        search = x.findall('.//' + self.namespace + 'search_score')
        for s in search:
            res = s.attrib['name']
            if res == 'expect':
                expect_val = s.attrib['value']
                if (expect_val!= None):
                    #print(res)
                    #print(expect_val)
                    return expect_val
                else:
                    return -1
    # def _table_two_rawad(self):
    #     summary = self.root.find('.//' + self.namespace + 'search_summary')
    #     if summary != None:
    #         parameters = summary.findall('.//' + self.namespace + 'parameter')
    #         for p in parameters:
    #             if re.match('variable_mod\\d+', p.attrib['name']):
    #                 curr = str(p.attrib['value'])
    #                 curr = curr.split()
    #                 if curr[1] != 'X':
    #                     self.modifications_in_file.append({
    #                         "amino": curr[1],
    #                         "value": curr[0],
    #                         "counter all": 0,
    #                         "counter mod": 0
    #                     })
    #
    #     print(self.modifications_in_file)
    #     #os._exit(2)

    # def _calc_modification_in_file(self):
    #     hist = dict()
    #     for pep in self.psm_list:
    #         pep = list(pep)     # string to list of letters
    #         for letter in pep:
    #             if letter in hist.keys():
    #                 hist[letter] = hist[letter] + 1
    #             else:
    #                 hist[letter] = 1
    #
    #     for l in self.modifications_in_file:
    #         amino = str(l["amino"])
    #         if amino in hist.keys():
    #             l["counter all"] = hist[amino]
    #
    #     print(self.modifications_in_file)
    #     os._exit(2)

    def _update_n_and_k_masses(self):
        """
        change the fields self.lysine_heavy_mass, self.lysine_light_mass
        self.n_heavy_mass, self.ln_light_mass
        NOTE: if n_light_mass = 0 at the end of this function i belive this is label mode so it is a good place to check
        if mode is label free

        """
        summary = self.root.find('.//' + self.namespace + 'search_summary')
        if summary != None:
            amino = summary.findall('.//' + self.namespace + 'aminoacid_modification')
            for a in amino:
                if a.attrib["aminoacid"] == "M":
                    self.m_mass = int(float(a.attrib['mass']))
                    self.m_mass_outPSM = "{:.2f}".format(float(a.attrib['mass']))
                if a.attrib["aminoacid"] == "C":
                    self.c_mass = int(float(a.attrib['mass']))
                    self.c_mass_outPSM = "{:.2f}".format(float(a.attrib['mass']))
                    if a.attrib["variable"] == "Y":
                        self.c_is_fixed = 0
                if a.attrib["aminoacid"] == "K":
                    if a.attrib["variable"] == "Y":
                        self.lysine_heavy_mass = int(float(a.attrib["mass"]))
                        self.lysine_heavy_mass_outPSM = "{:.2f}".format(float(a.attrib['mass']))

                    if a.attrib["variable"] == "N":
                        self.lysine_light_mass = int(float(a.attrib["mass"]))
                        self.lysine_light_mass_outPSM = "{:.2f}".format(float(a.attrib['mass']))
            term = summary.findall('.//' + self.namespace + 'terminal_modification')
            for t in term:
                if t.attrib["terminus"] == "N":
                    if t.attrib["variable"] == "Y":
                        self.n_heavy_mass = int(float(t.attrib["mass"]))
                        self.n_heavy_mass_outPSM = "{:.2f}".format(float(t.attrib['mass']))
                    if t.attrib["variable"] == "N":
                        self.n_light_mass = int(float(t.attrib["mass"]))
                        self.n_light_mass_outPSM = "{:.2f}".format(float(t.attrib['mass']))


    def _add_protein(self, x):
        """

        :param x: search hit
        add the protien attrib to self.protein_set
        """
        self.protein_set.add(x.attrib['protein'])
    def parse_outPSM(self,error_rate):
        hits_outPSM = self.root.findall('.//' + self.namespace + 'spectrum_query')
        for x in hits_outPSM:
            hit = x.find('.//' + self.namespace + 'search_hit')
            probability = hit.find('.//' + self.namespace + 'peptideprophet_result')
            if probability != None:
                probability = probability.attrib['probability']
            else:
                continue
            # print(probability)
            probability = float(probability)
            # print(probability)
            if probability < error_rate:
                continue
            expect = self._expect_calc(hit)
            expect = float(expect)
            num_matched_ions = hit.attrib["num_matched_ions"]
            if num_matched_ions != None and float(num_matched_ions) < MIN_MATCHED_IONS : #check min ions
                #print(num_matched_ions)
                continue
            modification_seq = ""
            mod = hit.find('.//' + self.namespace + 'modification_info')
            if mod!=None:
                modification_seq = mod.attrib['modified_peptide']
                k_type = ""
                if self.running_mode == "lysine":
                    k_type = self._k_peptide_type(str(modification_seq), 1)
                else:
                    k_type = self._k_peptide_type(str(modification_seq))
                if k_type == "bad kitty":
                    # print("catchhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
                    continue
            else:
                print(str(hit.attrib['peptide']))
                modification_seq = hit.attrib['peptide']
            seq = hit.attrib['peptide']
            prot = hit.attrib['protein']
            prot_alternative = hit.findall('.//' + self.namespace + 'alternative_protein')
            list_alternative = [prot]
            if prot_alternative:
                for y in prot_alternative:
                    curr = y.attrib['protein']
                    if curr not in list_alternative:
                        list_alternative.append(curr)
            start = hit.attrib['peptide_prev_aa']
            end = hit.attrib['peptide_next_aa']
            matched_ions = hit.attrib['num_matched_ions']
            total_ions = hit.attrib['tot_num_ions']
            assumed_chrage = int(x.attrib['assumed_charge'])
            precursor_neutral_mass = float(x.attrib['precursor_neutral_mass'])
            calc_neutral_pep_mass = float(hit.attrib['calc_neutral_pep_mass'])
            ppm = float(hit.attrib['massdiff'])
            ntt = float(hit.attrib['num_tol_term'])
            retention = float(x.attrib['retention_time_sec'])

            self.list_outPSM.append(OutPSM(seq,start, end, prot, list_alternative, probability,
                                           expect,matched_ions,total_ions, assumed_chrage,
                                           precursor_neutral_mass, calc_neutral_pep_mass,
                                           ppm, self.file_name, self.lysine_heavy_mass_outPSM,
                                           self.lysine_light_mass_outPSM, modification_seq,
                                           self.n_heavy_mass_outPSM,self.n_light_mass_outPSM,
                                           self.lysine_heavy_mass, self.lysine_light_mass,
                                           self.n_heavy_mass, self.n_light_mass, self.m_mass, self.c_mass,
                                           self.m_mass_outPSM, self.c_mass_outPSM, self.c_is_fixed, self.running_mode, ntt, retention))

    def _out_psm(self, error):
        self.parse_outPSM(error)



    def parse_dict(self, error_rate, swap):
        self._update_n_and_k_masses()
        error_rate = self._calc_error_rate(error_rate)
        # print (name_space)
        if self.running_mode == "variable":
            self.var_parse(error_rate)
            return
        self._out_psm(error_rate)
        hits = self.root.findall('.//' + self.namespace + 'search_hit')
        #dict_peptides = {}
        counter = 0
        for x in hits:

            probability = x.find('.//' + self.namespace + 'peptideprophet_result')
            if probability != None:
                probability = probability.attrib['probability']
            else:
                continue
            # print(probability)
            probability = float(probability)
            # print(probability)
            if probability < error_rate:
                continue

            expect = self._expect_calc(x)
            expect = float(expect)
            num_matched_ions = x.attrib["num_matched_ions"]
            if num_matched_ions != None and float(num_matched_ions) < MIN_MATCHED_IONS :
                #print(num_matched_ions)
                continue
            #print(expect)
            #modification_seq = x.find('.//' + self.namespace + 'modification_info')
            #if modification_seq != None:
             #   modification_seq = modification_seq.attrib['modified_peptide']
              #  self.pep_modification_set.add(modification_seq)
               # self.psm_list.append(modification_seq)

            if self.running_mode == "default":
                mod = x.find('.//' + self.namespace + 'modification_info')
                modification_seq = mod.attrib['modified_peptide']
                k_type = self._k_peptide_type(str(modification_seq))
                if k_type == "bad kitty":
                    #print("catchhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
                    continue
                heavy = x.find('.//' + self.namespace + 'xpressratio_result')
                if heavy != None:
                    heavy = heavy.attrib['heavy_area']
                    heavy = float(heavy)
                else:
                    continue
                light = x.find('.//' + self.namespace + 'xpressratio_result')
                if light != None:
                    light = light.attrib['light_area']
                    light = float(light)
                else:
                    continue


            elif self.running_mode == "label":
                mod = None
                matched_ions = x.attrib['num_matched_ions']
                label_free_res = x.find('.//' + self.namespace + 'xpresslabelfree_result')
                if label_free_res != None:
                    peak_area = label_free_res.attrib['peak_area']
                    peak_area = float(peak_area)
                    rt_seconds = label_free_res.attrib['peak_intensity_RT_seconds']
                    rt_seconds = float(rt_seconds)
                    peak_intensity = label_free_res.attrib['peak_intensity']
                    peak_intensity = float(peak_intensity)
                else:
                    continue

            # else:
            #     print("shouldnt get here!!")
            #     exit(1)
            if self.running_mode == "lysine":
                mod = x.find('.//' + self.namespace + 'modification_info')
                #print("bloop")
                #print(mod)
                if mod != None:
                    mod = mod.attrib['modified_peptide']
                    #print(mod)
                    k_type = self._k_peptide_type(mod, 1)
                    if k_type == "bad kitty":
                        continue
                    else:
                        heavy = x.find('.//' + self.namespace + 'xpressratio_result')
                        if heavy != None:
                            heavy = heavy.attrib['heavy_area']
                            heavy = float(heavy)
                        elif k_type == "no k":
                            heavy = 0
                        else:
                            continue
                        light = x.find('.//' + self.namespace + 'xpressratio_result')
                        if light != None:
                            light = light.attrib['light_area']
                            light = float(light)
                        elif k_type == "no k":
                            light = 0
                        else:
                            continue
                else:
                    continue

            modification_seq = x.find('.//' + self.namespace + 'modification_info')
            if modification_seq != None:
                modification_seq = modification_seq.attrib['modified_peptide']
                self.pep_modification_set.add(modification_seq)
                self.psm_list.append(modification_seq)
            else: # if pep doesnt have modification attrib, then add to set the seq itself
                #print(x.attrib['peptide'])
                s = x.attrib['peptide']
                self.pep_modification_set.add(s)
                self.psm_list.append(s)

            self._add_protein(x)


            seq = x.attrib['peptide']
            if seq in self.dict_peptides:
                self.dict_peptides[seq].add_counter()   # in all modes
                self.dict_peptides[seq].update_min_expect(expect)
                if self.running_mode == "lysine":
                    #print("here")
                    #self.little_test(str(mod))
                    k_type = self._k_peptide_type(mod, 1)
                    assert (k_type != "bad kitty")
                    self.dict_peptides[seq].add_heavy(heavy)
                    self.dict_peptides[seq].add_light(light)
                    if k_type == "heavy":
                        self.dict_peptides[seq].add_n_heavy()
                    elif k_type == "light":
                        self.dict_peptides[seq].add_n_light()
                    else:
                        assert (k_type == "no k")
                        self.dict_peptides[seq].add_no_k()

                    continue
                if self.running_mode == "default":
                    self.dict_peptides[seq].add_heavy(heavy)
                    self.dict_peptides[seq].add_light(light)
                    if mod != None:
                        mod = mod.attrib['modified_peptide']
                        self._modification_n(seq, mod)
                        #self.dict_peptides[seq].print_peptide()
                        continue
                elif self.running_mode == "label":
                    self.dict_peptides[seq].add_peak_area(peak_area)
                    self.dict_peptides[seq].add_avg_rt_seconds(rt_seconds)
                    self.dict_peptides[seq].add_peak_intensity(peak_intensity)
                    continue
                else:
                    print("shouldnt get here1!!")
                    exit(1)

            pep_type = x.attrib['num_tol_term']
            prot = x.attrib['protein']
            prot_alternative = x.findall('.//' + self.namespace + 'alternative_protein')
            list_alternative = [prot]
            if prot_alternative:
                for y in prot_alternative:
                    curr = y.attrib['protein']
                    if curr not in list_alternative:
                        list_alternative.append(curr)

                # print(list_alternative)
                # print(prot)
            # else:
            #     print("sould be NOne*************************************")
            #     print(prot_alternative)
            #     exit(1)

            start = x.attrib['peptide_prev_aa']
            end = x.attrib['peptide_next_aa']

            if self.running_mode == "default" or self.running_mode == "lysine":
                # -1 for peak_area, peak intensity, rt_seconds, ions
                self.dict_peptides[seq] = Peptide(seq, pep_type, prot, list_alternative, probability, start, end, heavy,
                                                  light, -1, -1, -1, -1, self.running_mode, expect, swap)
                if self.running_mode == "lysine":
                    if(k_type == "no k"):
                        #print(k_type)
                        self.dict_peptides[seq].add_no_k()
            elif self.running_mode == "label":
                # -1 for heavy and light
                self.dict_peptides[seq] = Peptide(seq, pep_type, prot, list_alternative, probability, start, end, -1,
                                                  -1, peak_area,peak_intensity, rt_seconds, matched_ions,
                                                  self.running_mode, expect, 0)
            else:
                print("shouldnt get here2!!")
                exit(1)
            if self.running_mode == "default":
                if mod != None:
                    #assert (self.running_mode == "default")
                    mod = mod.attrib['modified_peptide']
                    self._modification_n(seq, mod)
                #self.dict_peptides[seq].print_peptide()
            elif self.running_mode == "lysine":
                k_type = self._k_peptide_type(mod, 1)
                assert (k_type != "bad kitty")
                if k_type == "heavy":
                    self.dict_peptides[seq].add_n_heavy()
                elif k_type == "light":
                    self.dict_peptides[seq].add_n_light()

        #self._calc_modification_in_file()



class Variable(ParserPep):
    def __init__(self, input, mode, out):
        super().__init__(input, mode, out)
        self.var_modifications = dict() # update in func "update_var_modification", key = N[x]/N[w]M[y]/K[z] etc..
                                        # may be more than one variable in file - hence the N[x]/N[w]..
                                        # var = [mass (again),count all in file, count var in file]
                                        # example : N[35] : [35, 256, 200]
                                         #           N[29] : [ 29, 500, 499]
                                          #          K[162]: [162, 300, 120]
                                            # the "count all in file" for the n terminus is irelevamt caouse we take the psm
        ############################### all those 4 counters are for testing only - unused for the table
        self.count_k_all = 0            # count all k instances in all valid peptides
        self.count_n_all = 0
        self.count_k_var = 0        # count all K instances that have +val
        self.count_n_heavy = 0
        ###########################################################
        self.psm_table_2 = 0
        self.incomplete = 0 # num of bad kitty (mixed k)

    def _is_pep_ok(self,x, error_rate):
        probability = x.find('.//' + self.namespace + 'peptideprophet_result')
        if probability != None:
            probability = probability.attrib['probability']
        else:
         #   print("prob")
            return 0
        probability = float(probability)
        if probability < error_rate:
            #print("error rate")
            return 0
        num_matched_ions = x.attrib["num_matched_ions"]
        if num_matched_ions != None and float(num_matched_ions) < MIN_MATCHED_IONS:
            return 0
        #heavy = x.find('.//' + self.namespace + 'xpressratio_result')
        #if heavy == None:
         #   print("heavy")
          #  return 0
        #light = x.find('.//' + self.namespace + 'xpressratio_result')
        #if light == None:
         #   print("light")
          #  return 0

        return 1  # pep ok
    def update_dict_var_modification(self):
        """
        for variable mode we need to get the masses of all modes marked as "Y" in summery
        :return: no return, it updates the field self.var_modification
        """
        summary = self.root.find('.//' + self.namespace + 'search_summary')
        if summary != None:
            amino = summary.findall('.//' + self.namespace + 'aminoacid_modification')
            for a in amino:
                if a.attrib["variable"] == "Y":
                    re = str(a.attrib["aminoacid"]) + "[" + str(int(float(a.attrib["mass"]))) + "]"
                    #print(re)
                    self.var_modifications[re] = [int(float(a.attrib["mass"])), 0, 0]

            term = summary.findall('.//' + self.namespace + 'terminal_modification')
            for t in term:
                if t.attrib["variable"] == "Y":
                    re = str(t.attrib["terminus"]) + "[" + str(int(float(t.attrib["mass"]))) + "]"
                    #print (re)
                    self.var_modifications[re] = [int(float(t.attrib["mass"])), 0, 0]
        for key in list(self.var_modifications):
            if str(key).startswith("N"):
                new_key = str(key).replace("N", "n")
                #print(new_key)
                self.var_modifications[new_key] = self.var_modifications[key]
                del self.var_modifications[key]

        #print(self.var_modifications)
        #os._exit(8)



    def var_parse(self, error_rate):
        #print(error_rate)
        self.update_dict_var_modification()
        hits = self.root.findall('.//' + self.namespace + 'search_hit')
        #print("1")
        for x in hits:
            #print("2")
            if self._is_pep_ok(x, error_rate):
                #print("3")
                modification_seq = x.find('.//' + self.namespace + 'modification_info')
                if modification_seq != None:
                    modification_seq = modification_seq.attrib['modified_peptide']
                    modification_seq = str(modification_seq)
                    k_type = self._k_peptide_type(str(modification_seq))
                    #print(k_type)
                    if k_type == "bad kitty":
                        #print(modification_seq)
                        self.incomplete +=1
                        continue
                    self.psm_table_2 += 1
                    self.count_n_all += 1  # oded asked it to be the number of psm in pep, meaning the number of good peptides
                    for var in self.var_modifications.keys():
                        #print(str(var)[0])
                        if str(var)[0] in modification_seq:
                            curr: list = self.var_modifications[var]
                            curr[1] += modification_seq.count(str(var)[0]) #update count all
                            #re = str(var) + "[" + str(curr[0]) + "]"
                            #print(re)
                            curr[2] += modification_seq.count(var) #update count variable
                else:
                    self.psm_table_2 += 1
                    self.count_n_all += 1  # oded asked it to be the number of psm in pep, meaning the number of good peptides


                   # assert (self.n_heavy_mass)
                    #re = "n[" + str(self.n_heavy_mass) +"]"
                    #if modification_seq.startswith(re):
                     #  self.count_n_heavy += 1

                    #if "K" in modification_seq:
                     #   self.count_k_all += modification_seq.count("K")
                      #  #print(modification_seq.count(("K")))
                       # assert (self.lysine_heavy_mass)
                        #re = "K[" + str(self.lysine_heavy_mass) + "]"
                        #if re in modification_seq:
                         #   temp = modification_seq.count(re)
                            #print(modification_seq)
                          #  assert temp == modification_seq.count(("K"))
                           # self.count_k_var += temp
                            #print(modification_seq)
        for key in self.var_modifications.keys():
            if str(key)[0] == "n":
                #print("here to make a change")
                curr:list = self.var_modifications[key]
                curr[1] = self.psm_table_2


        #print(self.count_n_heavy)
        #print(self.count_n_all)
        #print(self.psm_table_2)
        #print(self.count_k_all)
        #print(self.count_k_var)
        #dict_to_list = [(v, k) for v, k in self.var_modifications.items()]
        #print(self.var_modifications.items())
        #print(dict_to_list)
        # {'seq60356_qe2': [4723, 2284, 2208, 1215, 5213, 2600], 'seq60357_qe2': [3934, 2080, 1754, 917, 3708, 2110]}
        #os._exit(8)
        print("num of incomplete peptides is " + str(self.incomplete))







