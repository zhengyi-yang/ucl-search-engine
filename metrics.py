#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 16:09:44 2017

@author: zhengyi
"""


from __future__ import division


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
    for i in xrange(1, len(ranked_list) + 1):
        f_measures.append(f_measure(ranked_list[:i + 1], relevant, alaph=0.5))
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


# TODO: NDCG
