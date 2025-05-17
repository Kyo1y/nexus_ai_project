import re

from itertools import groupby
from typing import List, Tuple, Union

class SplitCandidate:
    """Helper class for holding information on potential splits in string
    """
    start: int
    end: int
    text: str
    def __init__(self, start: int, end: int, text: str):
        self.start = start
        self.end = end
        self.text = text.strip()
    
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self):
        return f'{self.__class__.__name__}(start={self.start}, end={self.end}, text={self.text})'
    
    def __repr__(self) -> str:
        return self.__str__()

def find_split_candidates(input_str: str, split_keywords) -> List[SplitCandidate]:
    pattern = '|'.join(split_keywords)
    match_list = [match for match in re.finditer(pattern, input_str, re.IGNORECASE)]

    candidate_list = []
    for match in match_list:
        candidate = SplitCandidate(match.start(), match.end(), match.group().strip())
        candidate_list.append(candidate)
    return candidate_list

def merge_overlapping_ranges(ranges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        
    if not ranges:
        return []

    ranges.sort(key=lambda x: x[0])  # Sort ranges based on the start values
    merged_ranges = [ranges[0]]  # Always Tuple[int, int]

    for current_start, current_end in ranges[1:]:
        previous_start, previous_end = merged_ranges[-1]

        if current_start <= previous_end:  # Overlapping ranges
            merged_ranges[-1] = (previous_start, max(previous_end, current_end))
        else:
            merged_ranges.append((current_start, current_end))

    return merged_ranges

def find_matching_indices(s, brackets=[('(', ')')]):
    stack = []
    indices = []

    opening_chars = [pair[0] for pair in brackets]
    closing_chars = [pair[1] for pair in brackets]
    mapping = dict(zip(closing_chars, opening_chars))

    for i, char in enumerate(s):
        if char in opening_chars:
            stack.append((char, i))
        elif char in closing_chars:
            if stack and stack[-1][0] == mapping[char]:
                indices.append((stack.pop()[1], i))
        elif char in ["'", '"']:
            if stack and stack[-1][0] == char:
                indices.append((stack.pop()[1], i))
            else:
                stack.append((char, i))

    return merge_overlapping_ranges(indices)

def create_substrings(input_string: str, positions: List[Tuple[int, int]]) -> List[str]:
    """
    Create substrings from the input string based on the specified start and end positions.

    Parameters:
    - input_string (str): The input string from which substrings will be extracted.
    - positions (List[Tuple[int, int]]): A list of tuples representing start and end positions.

    Returns:
    - List[str]: A list of strings representing the substrings extracted from the input string.
    """
    results = []
    
    for start, end in positions:
        substring = input_string[start:end]
        results.append(substring)
    
    return results

def filter_candidates(candidates: List[SplitCandidate], escaped_ranges: List[Tuple[int, int]]):
    if not escaped_ranges:
        return candidates
    # Filters out idxs that are in the escaped range
    range_idx = 0
    start, end = escaped_ranges[range_idx]

    split_candidates = []
    for i, candidate_obj in enumerate(candidates):
        candidate_start = candidate_obj.start
        while candidate_start > end and range_idx < len(escaped_ranges):
            range_idx += 1
            if range_idx >= len(escaped_ranges):
                split_candidates += candidates[i:]
                break
            start, end = escaped_ranges[range_idx]


        # Only add if smaller than start
        if candidate_start < start:
            split_candidates.append(candidate_obj)
    return split_candidates

def convert_candidates_to_str_chunks(candidates: List[SplitCandidate], input_str: str, remove_split_word: bool = True) -> List[str]:
    
    idx_chunks = [(0, candidates[0].start)]
    for c_idx in range(len(candidates)):
        start = candidates[c_idx].end if remove_split_word else candidates[c_idx].start
        end = candidates[c_idx+1].start if c_idx != len(candidates) - 1 else len(input_str)
        idx_chunks.append((start, end))

    # Build chunks
    chunks = create_substrings(input_str, idx_chunks)
    return chunks

def group_chunks_by_operators(operators: List[str], chunks: List[str]):
    """
    Group chunks based on consecutive values in the operators list.

    Parameters:
    - operators (list): A list of strings representing operators.
    - chunks (list): A list of strings representing chunks to be grouped.

    Returns:
    - list of tuple: A list of tuples where the first value is the matched operator
                     and the second is the list of consecutive chunks.
    """
    grouped_data = []

    for operator, chunk_group in groupby(zip(operators, chunks), key=lambda x: x[0]):
        chunk_list = [chunk for _, chunk in chunk_group]
        grouped_data.append((operator, chunk_list))

    return grouped_data
