from collections import defaultdict
from decimal import Decimal as D
import heapq
from app.errors import DataError
from .values import number, parts


def evaluate(row):
    source, target = row['始点'], row['终点']
    min_width = number(row['最小净宽厘米'], 1, 1000)
    max_grade = number(row['最大纵坡百分比'], 0, 100)
    graph = defaultdict(list)
    blocked, seen = [], set()
    for raw in parts(row['路段']):
        road = raw.split(':')
        if len(road) != 5 or road[-1] not in {'开放', '封闭'}:
            raise DataError('ROAD_FORMAT', f'路段字段无效 {raw}')
        name, distance, width, grade, state = road
        a, sep, b = name.partition('>')
        if not sep or not a or not b or a == b or '>' in b or name in seen:
            raise DataError('ROAD_CONFLICT', f'路段标识无效或重复 {name}')
        seen.add(name)
        length = number(distance, D('0.01'), 100000)
        if state == '封闭' or number(width, 1, 1000) < min_width or abs(number(grade, -100, 100)) > max_grade:
            blocked.append((name, state if state == '封闭' else '坡宽超限', ''))
        else:
            graph[a].append((b, length))
    if source == target:
        return D(0), [('到达', source, '')]
    queue = [(D(0), (source,), ())]
    visited = set()
    while queue:
        distance, path, legs = heapq.heappop(queue)
        node = path[-1]
        if node in visited:
            continue
        visited.add(node)
        if node == target:
            return distance, [(f'{a} → {b}', leg, '米') for a, b, leg in legs] + blocked
        for adjacent, leg in graph[node]:
            if adjacent not in visited:
                heapq.heappush(queue, (distance+leg, path+(adjacent,), legs+((node, adjacent, leg),)))
    raise DataError('ROAD_UNREACHABLE', f'{source} 至 {target} 无满足坡宽约束的路径')
