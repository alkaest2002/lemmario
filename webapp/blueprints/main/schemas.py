import re
from pydantic import BaseModel, validator
from typing import List, Union
from datetime import datetime
from enum import Enum

class Pagination(BaseModel):
    
    words_n_all:     int                  = 0
    words_n_filter:  int                  = 0
    words_list:      List[str]            = []
    first_rec:       Union[str, datetime] = None
    last_rec:        Union[str, datetime] = None
    prev_rec:        Union[str, datetime] = None
    next_rec:        Union[str, datetime] = None
    is_first_page:   bool                 = True
    is_last_page:    bool                 = False
    offset_field:    str                  = 'lemma'
    offset_value:    Union[str, datetime] = None
    offset_dir:      str                  = 'next'
    filter_field:    str                  = 'lemma'
    filter_value:    Union[str, datetime] = None
    order_field:     str                  = 'lemma'
    order_dir:       str                  = 'ASC'


    @validator('offset_value', 'filter_value')
    def allowed_field_value(cls, v):
        if not re.sub("\s|'|\-","", v).isalnum():
            raise ValueError('illegal field value')
        return v

    @validator('offset_field', 'filter_field', 'order_field')
    def allowed_field(cls, v):
        if v not in ('lemma','visited'):
            raise ValueError('illegal field name')
        return v

    @validator('offset_dir')
    def must_be_asc_or_desc(cls, v):
        if v not in ('next','prev'):
            raise ValueError('illegal order by')
        return v

    @validator('order_dir')
    def must_be_next_or_prev(cls, v):
        if v not in ('ASC','DESC'):
            raise ValueError('illegal order by')
        return v
