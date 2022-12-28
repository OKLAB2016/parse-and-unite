class Peptide:
    """
    parsing pep.xml into dictionary
    the dict has key=seq and value= Peptide class
    """

    def __init__(self, seq, pep_type, prot, alternative, prob, start, end, heavy , light, peak_area, peak_intensity,
                 rt_seconds, ions, mode, expect, swap):
        self.seq: str = seq                   # attrib "peptide" of "search_hit" in xml
        self.pep_type: int = pep_type         # attrib "num_tol_term" of "search_hit in xml
        self.prot: str = prot                 # attrib "protein" of "search_hit" in xml
        self.alternative: list = alternative  # all allternative_protein.attrib(protein)
        self.prob: float = prob               # attrib  "probabilty" of "search_hit\ peptideprophet_result" in xml
        self.start: str = start               # attrib "peptide_prev_aa"  of "search_hit" in xml
        self.end: str = end                   # attrib "pepide_next_aa"  of "search_hit" in xml
        self.counter: int = 1                 # number of occurrences of the same seq in file
        self.n_heavy: int = 0                 # number of peptides with "n[35]" modifications
        self. n_light: int = 0                # number of peptides with "n[29]" modificationa
        self.heavy: float = heavy             # sum of all heavy_area - attrib of search_hit\ xpressratio_result
        self.light: float = light             # sum of all light_area - attrib of search_hit\ xpressratio_result
        self.peak_area: float = peak_area     # sum of all peak area for label-free mode
        self.peak_intensity: float = peak_intensity  # sum of all peak intensity for label-free mode
        self.rt_seconds: float = rt_seconds   # avg og all rt_seconds intensity for label-free mode
        self.ions: int = ions                 # number of matched ions - for label-free mode
        self.ratio: str = "0"                 # light / heavy. if heavy=0 ratio=-1
        self.mode: int = mode                 # is it free- label (==1) or not (==0)
        self.no_k: int = 0                    # used only for uniform n k running mode to sum up the ynmarked peps
        self.min_expect: float = expect               # attrib "expect value", taking the minimum value of all repetitions
        self.swap : int = swap # calc heavy/light instead light/heavy
        if self.mode == "default" or self.mode == "lysine":
            if self.swap:
                self._calc_ratio_swap()
            else:
                self._calc_ratio()

    def add_n_heavy(self):
        self.n_heavy += 1

    def add_n_light(self):
        self.n_light += 1

    def add_counter(self):
        self.counter += 1

    def add_heavy(self, new_heavy):
        self.heavy += new_heavy
        # recalcing ratio
        if self.swap:
            self._calc_ratio_swap()
        else:
            self._calc_ratio()

    def add_light(self, new_light):
        self.light += new_light
        # recalcing ratio
        if self.swap:
            self._calc_ratio_swap()
        else:
            self._calc_ratio()

    def add_no_k(self):
        self.no_k += 1

    def add_peak_area(self, new_peak):
        self.peak_area += new_peak

    def add_peak_intensity(self, new_intens):
        self.peak_intensity += new_intens

    def add_avg_rt_seconds(self, new_rt):
        sum_without_new = (self.counter - 1) * self.rt_seconds
        self.rt_seconds = (sum_without_new + new_rt) / self.counter

    def update_min_expect(self, expect: float):
        if expect == -1:
            """ -1 means no attrib expect found in repetition, so ignore this one"""
            return
        elif expect < self.min_expect:
            #assert (expect != -1)
            self.min_expect = expect
            #print(expect)


    def _calc_ratio(self):
        if self.heavy == 0 and self.light == 0:  # preventing dev in 0
            self.ratio = "0 dev 0"
        elif self.heavy == 0:
            assert self.light
            self.ratio = "num dev 0"
        else:
            assert self.heavy
            ratio: float = self.light/self.heavy
            str(ratio)
            self.ratio = ratio

    def _calc_ratio_swap(self):
        if self.heavy == 0 and self.light == 0:  # preventing dev in 0
            self.ratio = "0 dev 0"
        elif self.light == 0:
            self.ratio = "num dev 0"
        else:
            assert self.light
            ratio: float = self.heavy/self.light
            str(ratio)
            self.ratio = ratio


    # just for testing
    def print_peptide(self):
        print("seq is " + self.seq)
        #print("type is " + self.pep_type)
        #print("prot is " + self.prot)
        # cannot print srr with none-str type... so i used join to convert list to str
        #print("alternative is " + "".join(self.alternative))
        #print("prob is " + str(self.prob))
        #print("start is " + str(self.start))
        #print("end is " + str(self.end))
        print("counter is " + str(self.counter))
        print("heavy is " + str(self.heavy))
        print("light is " + str(self.light))
        print("ratio is " + str(self.ratio))
        print ("n heavy is " + str(self.n_heavy))
        print("n light is " + str(self.n_light))
        print("**********************")

    def class_to_list(self, mode):
        pep = []
        pep.append(self.seq)
        pep.append(self.pep_type)
        pep.append(self.prot)
        pep.append("".join(self.alternative))
        pep.append(self.prob)
        pep.append(self.start)
        pep.append(self.end)
        pep.append(self.counter)
        if mode == "default" or mode == "lysine":
            pep.append(self.n_heavy)
            pep.append(self.n_light)
            if mode == "lysine":
                pep.append(self.no_k)
            pep.append(self.heavy)
            pep.append(self.light)
            pep.append(self.ratio)
        elif mode == "label":
            pep.append(self.peak_area)
            pep.append(self.peak_intensity)
            pep.append(self.rt_seconds)
            pep.append(self.ions)

        pep.append(self.min_expect)
        return pep