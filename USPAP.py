
class USPAP:
    fields = dict()

    def __init__(self):
        self.fields["client"] = None
        self.fields["intended user(s)"] = None
        self.fields["the intended use"] = None
        self.fields["interest appraised"] = None
        self.fields["type and definition of value"] = None
        self.fields["the date of the report"] = None
        self.fields["the scope of work used to develop the appraisal"] = None
        self.fields["the extent of any significant appraisal assistance"] = None
        self.fields["methods and techniques"] = None
        self.fields["the reasons for excluding the sales comparison, cost, or income approach(es)"] = None
        self.fields["the subject sales and other transfers, agreements of sale, options, and listings"] = None  # can not find
        self.fields["value opinion(s) and conclusion(s)"] = None
        self.fields["signed certification"] = None

    def get_fields(self):
        return self.fields

