# General imports
import numpy as np
import pandas as pd
import itertools

# Biopython imports
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


# Dictionaries

one_hot_dict = {
    'A': [1, 0, 0, 0],
    'C': [0, 1, 0, 0],
    'G': [0, 0, 1, 0],
    'T': [0, 0, 0, 1],
    'N': [1/4, 1/4, 1/4, 1/4],
    'W': [1/2, 0, 0, 1/2],
    'S': [0, 1/2, 1/2, 0],
    'M': [1/2, 1/2, 0, 0],
    'K': [0, 0, 1/2, 1/2],
    'R': [1/2, 0, 1/2, 0],
    'Y': [0, 1/2, 0, 1/2], 
    'B': [0, 1/3, 1/3, 1/3],
    'D': [1/3, 0, 1/3, 1/3],
    'H': [1/3, 1/3, 0, 1/3],
    'V': [1/3, 1/3, 1/3, 0],
    'Z': [0, 0, 0, 0]
}

sense_complement_dict = {
    '+':'-', 
    '-':'+'
}

bases = list(one_hot_dict.keys())
integer_encoding_dict = {}
for x in range(len(bases)):
    integer_encoding_dict[bases[x]] = x

    
# Sequence encoding

def integer_encode(record, rcomp=False):
    """Function to integer encode a DNA sequence.
    
    Args:
      seq (seqrecord): seqrecord object containing a sequence of length L
      rcomp (bool): reverse complement the sequence before encoding
    
    Returns:
      result (np.array): array containing integer encoded sequence. Shape (1, L, 1)
    
    """
    # Reverse complement
    if rcomp:
        seq = record.seq.reverse_complement()
    else:
        seq = record.seq
    # Encode
    result = np.array([integer_encoding_dict.get(base) for base in seq])
    # Shape
    result = np.expand_dims(result, 0)
    result = np.expand_dims(result, 2)
    return result  


class SeqEncoding:
    """Encodes a single DNA sequence, or a set of DNA sequences all of which have the same length and sense.
    
    Args:
        records (list): list of seqrecord objects
        rcomp (bool): encode sequence reverse complement as well as original sequence
        sense (str): sense of sequence(s), '+' or '-'.
      
    Raises:
        ValueError: if sequences have unequal length.
    
    """
    def __init__(self, records, rcomp=False, sense=None):
        self.reverse_complemented = False
        self.check_equal_lens(records)
        self.len = len(records[0].seq)
        self.seqs = np.concatenate([integer_encode(record, rcomp=False) for record in records], axis=0)
        self.ids = np.array([record.id for record in records])
        self.names = np.array([record.name for record in records])
        self.senses = np.array([sense]*len(records))
        if rcomp:
            rcomp_encoded = np.concatenate([integer_encode(record, rcomp=True) for record in records], axis=0)
            self.seqs = np.concatenate([self.seqs, rcomp_encoded], axis=0)
            self.ids = np.tile(self.ids, 2)
            self.names = np.tile(self.names, 2)
            self.senses = np.append(self.senses, [sense_complement_dict[sense] for sense in self.senses])
            self.reverse_complemented = True
    def check_equal_lens(self, records):
        if len(records) > 1:
            lens = [len(record.seq) for record in records]
            if len(np.unique(lens)) != 1:
                raise ValueError("Cannot encode - sequences have unequal length!")

    
class MultiSeqEncoding:
    """Encodes multiple sets of sequences, each of which may have different length.
    
    Args:
        records (list): list of seqrecord objects
        rcomp (bool): encode sequence reverse complement as well as original sequence
        sense (str): sense of sequence(s), '+' or '-'.
        group_by_name (bool): group sequences by their name
    
    """
    def __init__(self, records, rcomp=False, sense=None, group_by_name=False):
        if (group_by_name) and (len(records)) > 1:
            records = self.group_by_name(records)
            self.seqs = [SeqEncoding(records, sense=sense, rcomp=rcomp) for records in records]
        else:
            self.seqs = [SeqEncoding([record], sense=sense, rcomp=rcomp) for record in records]
    def group_by_name(self, records):
        records_dict = {}
        for record in records:
            if record.name in records_dict.keys():
                records_dict[record.name].append(record)
            else:
                records_dict[record.name] = [record]
        return records_dict.values()
