import pandas as pd
import numpy as np
import itertools

from .encode import SeqGroups


def locate_sites(encoding, model, thresholded, scores=None):
    """ Function to locate potential binding sites given model predictions.
    
    Args:
        encoding (SeqEncoding): SeqEncoding object
        model (model): parameterized convolutional model
        thresholded (np.array): positions where the input sequence(s) match the input 
                                PWM(s) with a score above the specified threshold.
        scores (np.array): score for each potential binding site
      
    Returns:
        sites (pd.DataFrame): dataframe containing information on each potential binding site.
     
    """
    seq_idx = thresholded[0]
    pos_idx = thresholded[1]
    pwm_idx = thresholded[2]
    sites = pd.DataFrame({'id': encoding.ids[seq_idx],
                              'name':encoding.names[seq_idx],
                              'sense':encoding.senses[seq_idx],
                              'start': pos_idx,
                              'Matrix_id': model.Matrix_ids[pwm_idx]})
    sites['width'] = model.widths[pwm_idx]
    sites['end'] = sites['start'] + sites['width']
    if scores is not None:
        sites['score'] = scores
        sites['max_score'] = model.max_scores[pwm_idx]
        sites['frac_score'] = sites['score']/sites['max_score']
    return sites


def bin_sites_by_score(encoding, model, thresholded, scores, bins):
    """ Function to locate potential binding sites and bin them based on their score.
    
    Args:
        encoding (SeqEncoding): SeqEncoding object
        model (model): parameterized convolutional model
        thresholded (np.array): positions where the input sequence(s) match the input 
                                PWM(s) with a score above the specified threshold.
        scores (np.array): score for each potential binding site.
        bins (list): list of fractional values (0 to 1) to bin scores.
      
    Returns:
        sites (pd.DataFrame): dataframe containing information on each potential binding site.
     
    """
    seq_idx = thresholded[0]
    pwm_idx = thresholded[2]
    frac_scores = scores/model.max_scores[pwm_idx]
    binned_scores = pd.cut(frac_scores, np.concatenate([bins, [1]]))
    result = pd.crosstab(index = [model.Matrix_ids[pwm_idx], model.widths[pwm_idx]], 
                         columns = [encoding.ids[seq_idx], 
                                    encoding.names[seq_idx], 
                                    encoding.senses[seq_idx], 
                                    binned_scores])
    result = result.melt(ignore_index=False).reset_index()
    result.columns = ['Matrix_id', 'width', 'id', 'name', 'sense', 'bin', 'num']
    return result

                       
def count_sites(encoding, model, thresholded):
    """Function to count the number of matches per PWM.
        
    Args:
        encoding (SeqEncoding): SeqEncoding object
        model (model): parameterized convolutional model
        thresholded (np.array): positions where the input sequence(s) match the input 
                                PWM(s) with a score above the specified threshold.
      
    Returns:
        result (pd.DataFrame): dataframe containing number of matches per PWM.
     
    """
    seq_idx = thresholded[0]
    if len(seq_idx) == 0:
        return pd.DataFrame({'Matrix_id': [], 'width': [], 'id': [], 'name': [], 'sense': [], 
                            'num': []})
    else:
        pwm_idx = thresholded[2]
        widths = model.widths[pwm_idx]
        result = pd.crosstab(index = [model.Matrix_ids[pwm_idx], widths], 
                         columns = [encoding.ids[seq_idx], 
                                    encoding.names[seq_idx], 
                                    encoding.senses[seq_idx]])
        result = result.melt(ignore_index=False).reset_index()
        result.columns = ['Matrix_id', 'width', 'id', 'name', 'sense', 'num']
        return result


def find_sites_seq(encoding, model, threshold, outputs = ['sites'], score=False):
    """Function to predict binding sites on encoded sequence(s).
    
    Args:
        encoding (SeqEncoding): object of class SeqEncoding
        model (model): class PWMModel
        threshold (float or np.arange): threshold (from 0 to 1) to identify binding sites OR np.arange (with binned_counts=True).
        outputs (list): List containing the desired outputs - any combination of 'sites', 'counts', 'binned_counts' 
                        and 'stats'. For example: ['sites', 'counts'].
                        'sites' outputs binding site locations
                        'counts' outputs the total count of binding sites per PWM
                        'binned_counts' outputs the counts of binding sites per PWM binned by score
                        'stats' outputs the mean and standard deviation of the number of binding sites per PWM,
                         across multiple sequences.
        score (bool): output scores for binding sites. Only relevant if 'sites' is specified.
    
    Returns: 
        output (dict): dictionary containing specified outputs.
        
    """
    output = {}
    if 'binned_counts' in outputs:
        score = True
        assert type(threshold) == np.ndarray
        thresholded, scores = model.predict_with_threshold(encoding.seqs, min(threshold), score)
        output['binned_counts'] = bin_sites_by_score(encoding, model, thresholded, scores, threshold)
    else:
        thresholded, scores = model.predict_with_threshold(encoding.seqs, threshold, score)
    if 'sites' in outputs:
        output['sites'] = locate_sites(encoding, model, thresholded, scores)
    if ('counts'  in outputs) or ('stats' in outputs):
        counts = count_sites(encoding, model, thresholded)
    if 'counts' in outputs:
        output['counts'] = counts
    if 'stats' in outputs:
        stats = counts.groupby(['Matrix_id', 'width', 'sense', 'name']).agg([len, np.mean, np.std]).reset_index()
        stats.columns = ['Matrix_id', 'width', 'sense', 'name', 'len', 'avg', 'sd'] 
        output['stats'] = stats

    return output


def find_sites_in_groups(encoding, model, threshold, outputs=['sites'], score=False, combine_groups=False, sep_ids=False):
    """Function to predict binding sites on class SeqGroups.
    
    Args:
        encoding (SeqGroups): object of class SeqGroups
        model (model): class PWMModel
        threshold (float or np.arange): threshold (from 0 to 1) to identify binding sites OR np.arange (with binned_counts=True).
        outputs (list): List containing the desired outputs - any combination of 'sites', 'counts', 'binned_counts' 
                        and 'stats'. For example: ['sites', 'counts'].
                        'sites' outputs binding site locations
                        'counts' outputs the total count of binding sites per PWM
                        'binned_counts' outputs the counts of binding sites per PWM binned by score
                        'stats' outputs the mean and standard deviation of the number of binding sites per PWM,
                        across multiple sequences.
        score (bool): output scores for binding sites. Only relevant if 'sites' is specified.
        combine_groups (bool): combine outputs for multiple sequence groups into a single dataframe
        sep_ids (bool): separate outputs by sequence ID.
    
    Returns: 
        output (dict): dictionary containing specified outputs.
        
    """
    # Find binding sites per sequence or group of sequences
    inter_outputs = outputs.copy()
    if combine_groups and ('stats' in outputs):
        if 'counts' not in outputs:
            inter_outputs.append('counts')
        inter_outputs.remove('stats')
    output_per_seq = [find_sites_seq(seq, model, threshold, inter_outputs, score=score) for seq in encoding.seqs]
    # Concatenate binding sites
    output = {}
    for key in output_per_seq[0].keys():
        output[key] = pd.concat([x[key] for x in output_per_seq]).reset_index(drop=True)
    # Combine binding sites
    if combine_groups:
        if sep_ids:
            if 'counts' in output.keys():
                output['counts'] = output['counts'].groupby(['Matrix_id', 'width', 'sense', 'id']).num.sum().reset_index()
            if 'binned_counts' in output.keys():
                output['binned_counts'] = output['binned_counts'].groupby(['Matrix_id', 'width', 'sense', 'bin', 'id']).num.sum().reset_index()
        else:
            if 'counts' in output.keys():
                output['counts'] = output['counts'].groupby(['Matrix_id', 'width', 'sense']).num.sum().reset_index()
            if 'binned_counts' in output.keys():
                output['binned_counts'] = output['binned_counts'].groupby(['Matrix_id', 'width', 'sense', 'bin']).num.sum().reset_index()
        # Calculate stats
        if 'stats' in outputs:
            stats = output['counts'].groupby(['Matrix_id', 'width', 'sense']).agg([len, np.mean, np.std]).reset_index()
            stats.columns = ['Matrix_id', 'width', 'sense', 'len', 'avg', 'sd'] 
            output['stats'] = stats 
            if 'counts' not in outputs:
                del output['counts']
    
    return output


def scan_sequences(seqs, model, threshold, sense, rcomp=None, outputs=['sites'], score=False, combine_seqs=False, sep_ids=False):
    """Encode given sequences and predict binding sites on them.
    
    Args:
        seqs (list / str): list of seqrecord objects or fasta file
        
        model (model): class PWMModel
        threshold (float or np.arange): threshold (from 0 to 1) to identify binding sites OR np.arange (with binned_counts=True).
        sense (str): sense of sequence(s), '+' or '-'.
        rcomp (str): 'only' to encode the sequence reverse complement, or 'both' 
                     to encode the reverse complement as well as original sequence
        outputs (list): List containing the desired outputs - any combination of 'sites', 'counts', 'binned_counts' 
                        and 'stats'. For example: ['sites', 'counts'].
                        'sites' outputs binding site locations
                        'counts' outputs the total count of binding sites per PWM
                        'binned_counts' outputs the counts of binding sites per PWM binned by score
                        'stats' outputs the mean and standard deviation of the number of binding sites per PWM,
                        across multiple sequences.
        score (bool): output scores for binding sites. Only relevant if 'sites' is specified.
        combine_seqs (bool): combine outputs for multiple sequence groups into a single dataframe
        sep_ids (bool): separate outputs by sequence ID.
    
    Returns: 
        output (dict): dictionary containing specified outputs.
        
    """
    # Encode the sequences
    encoded = SeqGroups(seqs, rcomp=rcomp, sense=sense)
    # Find sites
    preds = find_sites_multiseq(encoded, model, threshold=threshold, outputs=outputs, combine_seqs=combine_seqs)
    return preds
    

# Analysis in windows

def get_tiling_windows_over_record(record, width, shift):
    """Function to get tiling windows over a sequence.
    
    Args:
        record (SeqRecord): SeqRecord object
        width (int): width of tiling windows
        shift (int): shift between successive windows
    
    Returns:
        windows (pd.DataFrame): windows covering input sequence
        
    """
    # Get start positions
    starts = list(range(0, len(record), shift))
    # Get end positions
    ends = [np.min([x + width, len(record)]) for x in starts]
    # Add sequence ID
    idxs = np.tile(record.id, len(starts))
    # Combine
    windows = pd.DataFrame({'id':idxs, 'start':starts, 'end':ends})
    return windows


def get_tiling_windows_over_genome(genome, width, shift=None):
    """Function to get tiling windows over a genome.
        
    Args:
        genome (list): list of SeqRecord objects
        width (int): width of tiling windows
        shift (int): shift between successive windows. By default the same as width.
    
    Returns:
        windows (pd.DataFrame): windows covering all sequences in genome
        
    """
    if shift is None:
        shift = width
    if len(genome) == 1:
        windows = get_tiling_windows_over_record(genome[0], width, shift)
    else:
        windows = pd.concat([get_tiling_windows_over_record(record, width, shift) for record in genome])
    return windows


def count_in_window(window, sites, matrix_id):
    """Function to calculate count of PWMs in subsequence.
    
    Args:
        window (pd.DataFrame): dataframe with columns id, start, end
        sites (pd.DataFrame): dataframe containing locations of binding sites
        matrix_id (str): selected PWM
    
    Returns:
        count (int): Number of binding sites for given PWM in selected window.

    """
    count = len(sites[(sites.Matrix_id==matrix_id) & (sites.id==window.id) & (sites.start >= window.start) & (sites.start < window.end)])
    return count


def count_in_sliding_windows(sites, genome, matrix_id, width, shift=None):
    """Function to count binding sites in sliding windows across a genome.
     
    Args:
        sites (pd.DataFrame): dataframe containing locations of binding sites
        genome (list): list of SeqRecord objects
        matrix_id (str): selected PWM
        width (int): width of tiling windows
        shift (int): shift between successive windows
    
    Returns:
        results (pd.DataFrame): dataframe containing number of binding sites per window
        
    """
    windows = get_tiling_windows_over_genome(genome, width, shift)
    windows['count'] = windows.apply(count_in_window, axis=1, args=(sites, matrix_id))
    windows.reset_index(inplace=True, drop=True)
    return windows