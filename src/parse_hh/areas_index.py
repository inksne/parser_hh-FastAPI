import json
import re
import difflib
import pathlib

from collections import defaultdict
from typing import Any



FALLBACK_IDS = ["113", "1"]  # Россия (113), Москва (1)

# префиксы/шаблоны, которые будут убираться из названий ввода
PREFIXES_RE = re.compile(
    r'^\s*(г\.|г |город |пос\.|пос |пгт |деревня |мкр |р-н |р\.н\.)\s*', flags=re.IGNORECASE
)

NON_ALNUM_RE = re.compile(r'[^0-9\w\sа-яё\-]', flags=re.IGNORECASE)  # сохранение кириллицф, цифр, дефиса



def normalize_name(name: str) -> str:
    if not name:
        return ''
    
    s = name.strip().lower()
    s = PREFIXES_RE.sub("", s)          # убрать "г.", "город" и т.п.
    s = s.replace(',', ' ')             # запятые -> пробел
    s = NON_ALNUM_RE.sub('', s)         # убрать точки, скобки и т.п.
    s = re.sub(r'\s+', ' ', s)          # сократить множественные пробелы

    return s.strip()



def build_area_index(area_json: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str]]:
    '''
    преобразует древовидный JSON областей в индекс:
      name_map: normalized_name -> list of entries {id, name, depth, path}
    возвращает (name_map, all_names_list)
    '''
    name_map: dict[str, list[dict[str, Any]]] = defaultdict(list)
    all_names: list[str] = []


    def dfs(node: dict[str, Any], path: list[str]):
        node_id = node.get("id")
        node_name = node.get("name", "")
        depth = len(path)  # корень depth=0 (страна), глубже = город/населённый пункт

        entry = {
            "id": str(node_id),
            "name": node_name,
            "depth": depth,
            "path": " > ".join(path + [node_name])
        }

        norm = normalize_name(node_name)

        if norm:
            name_map[norm].append(entry)
            all_names.append(norm)

        for child in node.get("areas", []):
            dfs(child, path + [node_name])


    for root in area_json:
        dfs(root, [])

    # уникальные all_names
    all_names = sorted(set(all_names))
    return name_map, all_names



def choose_best_candidate(candidates: list[dict[str, Any]]) -> list[str]:
    '''
    возвращает список id лучших кандидатов среди candidates
    логика: выбираем записи с максимальной глубиной (глубже = обычно город),
    если несколько одинаковой глубины — возвращаем все их id (HH допускает несколько)
    '''
    if not candidates:
        return []
    
    max_depth = max(c["depth"] for c in candidates)
    best = [c for c in candidates if c["depth"] == max_depth]

    # уникальные ids
    return list({c["id"] for c in best})



class AreaResolver:
    def __init__(self, name_map: dict[str, list[dict[str,Any]]], all_names: list[str]) -> None:
        self.name_map = name_map
        self.all_names = all_names


    def resolve(self, user_input: str) -> list[str]:
        '''преобразует строку пользователя в список id area. fallback -> FALLBACK_IDS'''
        if not user_input:
            return FALLBACK_IDS[:]

        norm = normalize_name(user_input)
        if not norm:
            return FALLBACK_IDS[:]

        # точное совпадение
        if norm in self.name_map:
            candidates = self.name_map[norm]
            return choose_best_candidate(candidates)


        # пробуем точное совпадение по частям (например "москва район" -> "москва")
        parts = [p for p in norm.split(' ') if p]
        for part in reversed(parts):  # начиная с наиболее специфичной части
            if part in self.name_map:
                return choose_best_candidate(self.name_map[part])


        # fuzzy match по словарю имён (difflib)
        # cutoff можно настроить: 0.75 — строгий, 0.6 — мягкий
        matches = difflib.get_close_matches(norm, self.all_names, n=3, cutoff=0.75)
        if matches:
            best_norm = matches[0]
            return choose_best_candidate(self.name_map.get(best_norm, []))


        return FALLBACK_IDS[:]



def load_area_resolver_from_file(path: str) -> AreaResolver:
    p = pathlib.Path(path)
    raw = json.loads(p.read_text(encoding='utf-8'))
    name_map, all_names = build_area_index(raw)

    return AreaResolver(name_map, all_names)