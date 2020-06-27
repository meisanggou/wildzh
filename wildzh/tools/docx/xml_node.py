# !/usr/bin/env python
# coding: utf-8


__author__ = 'zhouhenglc'


def get_node(p_node, node_name):
    f =  filter(lambda x: x.nodeName == node_name, p_node.childNodes)
    return list(f)


def _get_one_node(p_node, node_name):
    children = get_node(p_node, node_name)
    if len(children) != 1:
        raise RuntimeError("Fond not 1(is %s) %s" % (len(children), node_name))
    return children[0]


def get_deep_node(p_node, node_name):
    _names = node_name.split(".")
    p_nodes = [p_node]
    for name in _names:
        p_nodes = get_node(p_nodes[0], name)
        if len(p_nodes) <= 0:
            return []
    return p_nodes


def get_deep_one_node(p_node, node_name):
    nodes = get_deep_node(p_node, node_name)
    return nodes[0]
