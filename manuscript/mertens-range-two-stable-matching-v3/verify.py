import itertools
import json
import math
from fractions import Fraction

OFFSETS = (1, 2, -1, -2)
RANKINGS = tuple(itertools.permutations(range(4)))


def rank(ranking, offset):
    return ranking[OFFSETS.index(offset)] if offset else 4


def geometric_assignments(length):
    assignments = []
    for displacement in itertools.product(range(-2, 3), repeat=length):
        targets = [index + value for index, value in enumerate(displacement) if value]
        if len(targets) != len(set(targets)):
            continue
        if any(value and 0 <= index + value < length and
               displacement[index + value] != -value
               for index, value in enumerate(displacement)):
            continue
        assignments.append(displacement)
    return assignments


def certified(word, displacement):
    for left in range(len(word)):
        for right in range(left + 1, min(len(word), left + 3)):
            distance = right - left
            if displacement[left] == distance:
                continue
            if (rank(word[left], displacement[left]) < rank(word[left], distance) or
                    rank(word[right], displacement[right]) < rank(word[right], -distance)):
                continue
            return False
    return True


def buffer_pairs(occupied):
    pairs = []
    singles = []
    for half, center in [((0, 1, 2), 2), ((3, 4, 5), 3)]:
        free = [index for index in half if index not in occupied]
        if len(free) % 2:
            free.remove(center)
            singles.append(center)
        pairs.extend(zip(free[::2], free[1::2]))
    if len(singles) == 2:
        pairs.append(tuple(singles))
        singles.clear()
    return pairs, singles


def preferred_ranking(displacement):
    return next(ranking for ranking in RANKINGS if rank(ranking, displacement) == 0)


def close_word(word, displacement):
    length = len(word)
    size = length + 6
    partners = list(range(size))
    occupied = set()
    for index, value in enumerate(displacement):
        if not value:
            continue
        target = (index + value) % size
        partners[index] = target
        if target >= length:
            assert target - length in (0, 1, 4, 5)
            assert target - length not in occupied
            occupied.add(target - length)
            partners[target] = index
    pairs, singles = buffer_pairs(occupied)
    for left, right in pairs:
        partners[length + left] = length + right
        partners[length + right] = length + left
    rankings = list(word)
    for index in range(length, size):
        partner = partners[index]
        if partner == index:
            rankings.append(RANKINGS[0])
        else:
            offset = next(offset for offset in OFFSETS if (index + offset) % size == partner)
            rankings.append(preferred_ranking(offset))
    assert all(partners[partners[index]] == index for index in range(size))
    for index in range(size):
        assignment_rank = 4 if partners[index] == index else rank(
            rankings[index], next(offset for offset in OFFSETS
                                  if (index + offset) % size == partners[index]))
        for offset in OFFSETS:
            other = (index + offset) % size
            if other == partners[index]:
                continue
            other_rank = 4 if partners[other] == other else rank(
                rankings[other], next(value for value in OFFSETS
                                      if (other + value) % size == partners[other]))
            assert not (rank(rankings[index], offset) < assignment_rank and
                        rank(rankings[other], -offset) < other_rank)
    return len(singles)


def exclusive_triangle(word):
    cycles = ((0, 1, 2), (0, 2, 1))
    for cycle in cycles:
        if all(rank(word[index], cycle[(position - 1) % 3] - index) == 0 and
               rank(word[index], cycle[(position + 1) % 3] - index) == 1
               for position, index in enumerate(cycle)):
            return True
    return False


def cycle_matchings(size, distance):
    def extend(remaining, pairs):
        if not remaining:
            yield dict(pairs)
            return
        vertex, *others = remaining
        yield from extend(others, pairs + [(vertex, vertex)])
        for partner in others:
            separation = min((vertex - partner) % size, (partner - vertex) % size)
            if separation <= distance:
                yield from extend([value for value in others if value != partner],
                                  pairs + [(vertex, partner), (partner, vertex)])
    yield from extend(list(range(size)), [])


def nearest_neighbor_stable(profile, partners):
    size = len(profile)
    def preference(vertex, partner):
        if vertex == partner:
            return 2
        offset = 1 if (partner - vertex) % size == 1 else -1
        return 0 if profile[vertex] == offset else 1
    for vertex in range(size):
        neighbor = (vertex + 1) % size
        if partners[vertex] != neighbor:
            if (preference(vertex, neighbor) < preference(vertex, partners[vertex]) and
                    preference(neighbor, vertex) < preference(neighbor, partners[neighbor])):
                return False
    return True


def range_one_checks():
    results = []
    for size in range(3, 10):
        matchings = list(cycle_matchings(size, 1))
        failures = []
        for profile in itertools.product((-1, 1), repeat=size):
            if not any(nearest_neighbor_stable(profile, partners) for partners in matchings):
                failures.append(profile)
        assert len(failures) == (2 if size % 2 else 0)
        assert all(len(set(profile)) == 1 for profile in failures)
        results.append({'size': size, 'profiles': 2 ** size, 'unsolvable': len(failures)})
    return results


def corrected_constant_check():
    e_lower = Fraction(2718, 1000)
    e_upper = Fraction(2719, 1000)
    partial = sum((Fraction(1, math.factorial(index)) for index in range(8)), Fraction())
    remainder = Fraction(1, math.factorial(8)) * Fraction(9, 8)
    assert e_lower < partial and partial + remainder < e_upper
    integral_zero_one = sum((Fraction((-1) ** index, math.factorial(index)) /
                             (Fraction(index) + Fraction(3, 4)) for index in range(6)), Fraction())
    root_lower = [Fraction(value, 1000) for value in (840, 759, 707, 668, 638, 614, 594)]
    assert all(value ** 4 * (index + 2) < 1 for index, value in enumerate(root_lower))
    gamma_lower = integral_zero_one + sum((value * (e_upper ** (-index) -
                          e_lower ** (-index - 1))
                          for index, value in enumerate(root_lower, start=1)), Fraction())
    assert gamma_lower > Fraction(6, 5)
    assert Fraction(6, 5) ** 4 > 2
    return {'method': 'rational lower integration bounds for Gamma(3/4)',
            'gamma_three_quarters_lower_bound': str(gamma_lower),
            'conclusion': 'Gamma(3/4) > 6/5 > 2^(1/4); the corrected coefficient exceeds the proposed coefficient.'}


def main():
    counts = {}
    forbidden = []
    closed = 0
    ranking_weights = {ranking: index + 1 for index, ranking in enumerate(RANKINGS)}
    weighted_counts = {}
    excluded_weight = 0
    for length in range(4):
        assignments = geometric_assignments(length)
        count = 0
        weight_count = 0
        for word in itertools.product(RANKINGS, repeat=length):
            witness = next((displacement for displacement in assignments
                            if certified(word, displacement)), None)
            if witness is None:
                assert length == 3
                assert exclusive_triangle(word)
                forbidden.append(word)
                excluded_weight += math.prod(ranking_weights[ranking] for ranking in word)
            else:
                count += 1
                weight_count += math.prod(ranking_weights[ranking] for ranking in word)
                if length:
                    close_word(word, witness)
                    closed += 1
                if length == 3:
                    assert not exclusive_triangle(word)
        counts[str(length)] = count
        weighted_counts[str(length)] = weight_count
    assert counts == {'0': 1, '1': 24, '2': 576, '3': 13808}
    assert len(forbidden) == 16
    weight_total = sum(ranking_weights.values())
    assert weight_total == 300
    assert weighted_counts['0'] == 1
    assert weighted_counts['1'] == weight_total
    assert weighted_counts['2'] == weight_total ** 2
    assert weighted_counts['3'] + excluded_weight == weight_total ** 3
    layouts = []
    for bits in itertools.product((False, True), repeat=4):
        occupied = {index for index, bit in zip((0, 1, 4, 5), bits) if bit}
        pairs, singles = buffer_pairs(occupied)
        covered = [index for pair in pairs for index in pair] + singles + list(occupied)
        assert sorted(covered) == list(range(6))
        assert all(0 < abs(left - right) <= 2 for left, right in pairs)
        assert len(singles) <= 1 and all(index in (2, 3) for index in singles)
        layouts.append({'occupied': sorted(occupied), 'pairs': pairs, 'singles': singles})
    print(json.dumps({
        'arithmetic': 'exact integers and exhaustive finite enumeration',
        'open_word_counts': counts,
        'three_site_words': 24 ** 3,
        'excluded_three_site_words': len(forbidden),
        'excluded_words_description': 'exactly the two exclusive orientations with all exterior orders',
        'cyclic_closures_checked': closed,
        'cyclic_sizes_checked': [7, 8, 9],
        'buffer_masks_checked': len(layouts),
        'buffer_layouts': layouts,
        'all_length_coverage': 'The note proves the two injections and bounded logarithmic defect for every length.',
        'finite_scope': 'Exhaustive open-word counts for lengths 0 through 3, one closure for every certified word of lengths 1 through 3, and every buffer occupancy mask.',
        'weighted_law': {'ranking_weights': list(ranking_weights.values()),
                           'normalizing_weight': weight_total,
                           'certified_weight_numerators': weighted_counts,
                           'excluded_three_site_weight_numerator': excluded_weight,
                           'denominator_at_length_m': '300^m'},
        'range_one_cycles': range_one_checks(),
        'corrected_complete_graph_coefficient': corrected_constant_check()
    }, indent=2))


if __name__ == '__main__':
    main()
