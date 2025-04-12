# -*- coding: utf-8 -*- 
"""Ref包初始化文件""" 
 
from .ref_core import RefCore 
 
__all__ = ['RefCore'] 

def init_file_monitor():
    """Initialize file monitoring system"""
    print("Ref file monitoring system initialized")
    return True
