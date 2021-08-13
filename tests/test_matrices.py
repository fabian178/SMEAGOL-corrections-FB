from smeagol.matrices import *
import os
import pandas as pd
from smeagol.utils import equals


script_dir = os.path.dirname(__file__)
rel_path = "data"
data_path = os.path.join(script_dir, rel_path)


def test_check_ppm():
    probs = np.array([[0, 0, 0, 1], [.5, .5, 0, 0], [-.1, .6, .1, .2]])
    with pytest.raises(ValueError):
        check_ppm(probs)
    probs = np.array([[0, 0, 0, 1], [.5, 1.5, 0, 0], [.1, 2.6, .1, .2]])
    with pytest.raises(ValueError):
        check_ppm(probs)
    probs = np.array([[0, .5, .1], [0, .5, .6], [0, 0, .1], [1, 0, .2]])
    with pytest.raises(ValueError):
        check_ppm(probs)
    probs = np.array([[0, 0, 0, 1], [.5, .5, 0, 0], [.1, .6, .1, .2]])
    check_ppm(probs)


def test_check_pfm():
    freqs = np.array([[0, 0, 0, 10], [.5, .5, 0, 0], [1.1, .6, .2, 1]])
    with pytest.raises(ValueError):
        check_pfm(freqs)
    freqs = np.array([[0, 0, 0, 10], [5, 5, 0, 0], [1, -6, 2, 1]])
    with pytest.raises(ValueError):
        check_pfm(freqs)
    probs = np.array([[0, 5, 1], [0, 5, 6], [0, 0, 1], [10, 0, 1]])
    with pytest.raises(ValueError):
        check_ppm(probs)
    

def test_check_pwm():
    weights = np.array([[-6.65821148, -6.65821148, -6.65821148,  1.98924694],
                    [ 0.99284021,  0.99284021, -6.65821148, -6.65821148],
                    [-1.30065948,  1.25467785, -0.31836148, -1.30065948]])
    check_pwm(weights)
    with pytest.raises(ValueError):
        check_pwm(np.transpose(weights))


def test_normalize_pm():
    probs = np.array([[0.1, 0.1, 0.1, 0.7], [.5, .48, 0.01, 0.01], [.1, .6, .1, .2]])
    assert normalize_pm(probs) == probs
    probs = np.array([[0.1, 0.1, 0.1, 0.8], [.5, .48, 0.01, 0.01], [.1, .6, .2, .2]])
    expected = np.array([[0.09090909, 0.09090909, 0.09090909, 0.72727273], 
                         [.5, .48, 0.01, 0.01],
                         [.1, .6, .1, .2]])
    assert equals(normalize_pm(probs), expected)


def test_entropy():
    probs = np.array([[0.1, 0.1, 0.1, 0.7], [.5, .48, 0.01, 0.01], [.1, .6, .1, .2]])
    assert equals(entropy(probs[0]), 1.3567796494470394)
    assert equals(entropy(probs), 4.068876338442915)


def test_position_wise_ic():
    probs = np.array([[0.1, 0.1, 0.1, 0.7], [.5, .48, 0.01, 0.01], [.1, .6, .1, .2]])
    expected = [0.6432203505529606, 0.8588539054587927, 0.42904940554533133]
    assert equals(position_wise_ic(probs), expected)
    

def test_matrix_conversions():
    freqs = np.array([[0, 0, 0, 10], [5, 5, 0, 0], [1, 6, 2, 1]])
    probs = pfm_to_ppm(freqs, pseudocount = 1)
    expected = np.array([1/14, 1/14, 1/14, 11/14], 
                        [6/14, 6/14, 1/14, 1/14], 
                        [2/14, 7/14, 3/14, 2/14])
    assert equals(probs, expected)
    weights = ppm_to_pwm(probs)
    expected = np.array([-5.807354922057605, -5.807354922057605, -5.807354922057605, -2.347923303420307],
                        [-3.222392421336448, -3.222392421336448, -5.807354922057605, -5.807354922057605],
                        [-4.807354922057605, -3, -4.222392421336448, -4.807354922057605])
    assert equals(weights, expected)
    assert equals(pwm_to_ppm(weights), probs)
    

def test_trim_ppm():
    probs = np.array([[0.1, 0.1, 0.1, 0.7], 
                      [.5, .48, 0.01, 0.01], 
                      [.2, .4, .2, .2], 
                      [0.1, 0.1, 0.1, 0.7],
                      [.2, .4, .2, .2]])
    result = trim_ppm(probs, frac_threshold = 0.05)
    expected = np.array([[0.1, 0.1, 0.1, 0.7], 
                         [.5, .48, 0.01, 0.01], 
                         [.2, .4, .2, .2], 
                         [0.1, 0.1, 0.1, 0.7]])
    assert equals(result, expected) 


def test_matrix_correlation():
    X = np.array([[-1.32192809, -1.32192809, -1.32192809,  1.48542683],
                  [ 1.        ,  0.94110631, -4.64385619, -4.64385619],
                  [-1.32192809,  1.26303441, -1.32192809, -0.32192809]])
    Y = np.array([[-1.32192809, -1.32192809, -1.32192809,  1.48542683],
                  [ 1.        ,  0.94110631, -4.64385619, -4.64385619],
                  [-3.64385619,  1.84799691, -3.05889369, -2.32192809]])
    result = matrix_correlation(X, Y)
    assert equals(result, 0.91069616)
    Y = np.array([[-1.32192809, -1.32192809, -1.32192809,  1.48542683],
                  [ 1.        ,  0.94110631, -4.64385619, -4.64385619]])
    with pytest.raises(ValueError):
        matrix_correlation(X, Y)


def test_ncorr():
    X = np.array([[-1.30065948, -6.65821148,  1.668218  , -1.30065948],
                  [ 0.99284021,  0.99284021, -6.65821148, -6.65821148],
                  [ 0.26065175,  0.6727054 , -1.30065948, -0.31836148]])
    Y = np.array([[-0.99106688, -1.97336487, -0.41205364,  1.31654155],
                  [-7.33091688,  0.99551261,  0.80350944, -1.97336487],
                  [ 1.57897621, -0.41205364, -7.33091688, -1.97336487],
                  [ 0.        ,  0.        ,  0.32013481, -0.41205364],
                  [-0.99106688, -1.97336487,  1.31654155, -0.41205364]])
    result = ncorr(X, Y, min_overlap=3)
    assert equals(result, 0.25069190635147276)
    result = ncorr(X, Y, min_overlap=1)
    assert equals(result, 0.13176571002819804)
    result = ncorr(Y, X, min_overlap=1)
    assert equals(result, 0.13176571002819804)

    
def test_pairwise_ncorrs():
    df = pd.read_hdf(os.path.join(data_path, 'test_pwms.hdf5'), key='data')
    result = pairwise_ncorrs(list(df.weights))
    expected = np.array([[1, 0.2506919063514727, 0.9871733730221669],
                         [0.2506919063514727, 1, 0.21411930243854532],
                         [0.9871733730221669, 0.21411930243854532, 1]])
    assert equals(result, expected) 


def test_choose_representative_pm():
    df = pd.read_hdf(os.path.join(data_path, 'test_pwms.hdf5'), key='data')
    result = choose_representative_pm(df)
    assert result == 'x'
    result = choose_representative_pm(df.iloc[1:, :])
    assert result == 'z'

    
def test_cluster_pms():
    df = pd.read_hdf(os.path.join(data_path, 'test_pwms.hdf5'), key='data')
    result = cluster_pms(df, n_clusters=2, sims=None, weight_col='weight')
    assert type(result.clusters) == list
    assert len(result.clusters) == 3
    assert type(result.reps) == list
    assert len(result.reps) == 2
    assert type(result.min_ncorr) == list
    assert len(result.min_ncorr) == 2