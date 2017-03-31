#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 16:09:44 2017

@author: zhengyi
"""


from __future__ import division
from math import pow, log


def precision_recall(retrieved, relevant):
    retrieved_set = set(retrieved)
    relevant_set = set(relevant)

    # retrieved and relevant
    a = len(retrieved_set.intersection(relevant_set))
    precision = a / len(retrieved_set)
    recall = a / len(relevant_set)

    return precision, recall


def f_measure(retrieved, relevant, alaph=0.5):
    p, r = precision_recall(retrieved, relevant)
    f = 1 / (alaph / p + (1 - alaph) / r)

    return f


def precision_recall_curves(ranked_list, relevant):
    precisions = []
    recalls = []

    for i in xrange(len(ranked_list)):
        p, r = precision_recall(ranked_list[:i + 1], relevant)
        precisions.append(p)
        recalls.append(r)

    return precisions, recalls


def f_measure_curves(ranked_list, relevant, alaph=0.5):
    f_measures = []
    for i in xrange(len(ranked_list)):
        f_measures.append(f_measure(ranked_list[:i + 1], relevant, alaph))
    return f_measures


def average_precision(ranked_list, relevant):
    '''
    Average of precisions at relevant documents
    '''
    precisions = precision_recall_curves(ranked_list, relevant)[0]

    return sum(precisions) / len(precisions)


def k_precision(retrieved, relevant, ks):
    '''
    Precision at rank k for a list of k values
    '''
    return {k: precision_recall(retrieved[:k], relevant)[0] for k in ks}


def expected_search_length(ranked_list, relevant):
    '''
    Number of non-relevant documents ranked before seeing the 1st relevant document
    '''
    relevant_set = set(relevant)
    for i, r in enumerate(ranked_list):
        if r in relevant_set:
            break
    return i


def reciprocal_rank(ranked_list, relevant):
    '''
    Reciprocal of the rank at which the first relevant document is retrieved
    '''
    return 1 / (expected_search_length(ranked_list, relevant) + 1)


def average_overlap(rank1, rank2, depth=None):
    '''
    Compute the average overlap over 2 ranked lists
    Ref: https://ragrawal.wordpress.com/2013/01/18/comparing-ranked-list/
    '''
    rank1, rank2 = sorted([rank1, rank2], key=len, reverse=True)
    l2 = len(rank2)

    sum_ = 0

    if depth is None:
        depth = l2
    elif depth > l2:
        raise ValueError('depth too large')

    for i in xrange(depth):
        intersection = set.intersection(set(rank1[:i + 1]), set(rank2[:i + 1]))
        sum_ += len(intersection) / (i + 1)

    return sum_ / depth


def rbo(l1, l2, p=0.9):
    '''
        Calculates Ranked Biased Overlap (RBO) score. 
        l1 -- Ranked List 1
        l2 -- Ranked List 2
        Ref: http://www.williamwebber.com/research/papers/wmz10_tois.pdf
    '''
    if l1 == None:
        l1 = []
    if l2 == None:
        l2 = []

    (s, S), (l, L) = sorted([(len(l1), l1), (len(l2), l2)])

    if s == 0:
        return 0

    # Calculate the overlaps at ranks 1 through l
    # (the longer of the two lists)
    ss = set()  # contains elements from the smaller list till depth i
    ls = set()  # contains elements from the longer list till depth i
    x_d = {0: 0}
    sum1 = 0
    for i in range(l):
        x = L[i]
        y = S[i] if i < s else None

        # if two elements are same then
        # we don't need to add to either of the set
        if x == y:
            x_d[i + 1] = x_d[i] + 1
        # else add items to respective list
        # and calculate overlap
        else:
            ls.add(x)
            if y != None:
                ss.add(y)
            x_d[i + 1] = x_d[i] + (1 if x in ss else 0) + (1 if y in ls else 0)
        # calculate average overlap
        sum1 += x_d[i + 1] / (i + 1) * pow(p, i + 1)

    sum2 = 0
    for i in range(l - s):
        d = s + i + 1
        sum2 += x_d[d] * (d - s) / (d * s) * pow(p, d)

    sum3 = ((x_d[l] - x_d[s]) / l + x_d[s] / s) * pow(p, l)

    # Equation 32
    rbo_ext = (1 - p) / p * (sum1 + sum2) + sum3
    return rbo_ext


def rbd(rank1, rank2, p=0.9):
    '''
    Compute the rank-biased distance over 2 ranked lists

    '''
    return 1 - rbo(rank1, rank2, p)


def ndcg(retrieved, relevant, dcg_type=0):
    def _dcg(rank_rel):
        result = 0.
        for i, rel in enumerate(rank_rel):
            if dcg_type == 0:
                result += rel / log(i + 2, 2)
            if dcg_type == 1:
                result += (2**rel - 1) / log(i + 2, 2)
        return result

    def _idcg(rank_rel):
        return _dcg(sorted(rank_rel, reverse=True))

    def _ndcg(rank_rel):
        return _dcg(rank_rel) / _idcg(rank_rel)

    rel_dict = {r: 1 / (i + 1) for i, r in enumerate(relevant)}
    rank_rel = [rel_dict.get(r, 0) for r in retrieved]
    return _ndcg(rank_rel)
