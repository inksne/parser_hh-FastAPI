import json
import re
import difflib
import pathlib
from collections import defaultdict
from typing import Any



PREFIXES_RE = re.compile(
    r'^\s*(ст\. |ст |станция |м\.\s*|м |г\.\s*|г |город )\s*', flags=re.IGNORECASE
)
NON_ALNUM_RE = re.compile(r'[^0-9\w\sа-яё\-]', flags=re.IGNORECASE)



def normalize_name(name: str) -> str:
    if not name:
        return ''
    s = name.strip().lower()
    s = PREFIXES_RE.sub("", s)
    s = s.replace(',', ' ')
    s = NON_ALNUM_RE.sub('', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()



def build_metro_index(metro_json: list[dict[str, Any]]
                     ) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    '''
    преобразует JSON метро в индекс:
      name_map: normalized_station_name -> list of entries {
          id, station_name, city_id, city_name, line_id, line_name, path, depth}
    возвращает (name_map, all_names)
    '''
    name_map: dict[str, list[dict[str, Any]]] = defaultdict(list)
    all_names: list[str] = []


    for city in metro_json:
        city_id = str(city.get("id", ""))
        city_name = city.get("name", "")
        for line in city.get("lines", []):
            line_id = str(line.get("id", ""))
            line_name = line.get("name", "")
            for station in line.get("stations", []):
                station_id = str(station.get("id", ""))
                station_name = station.get("name", "")
                # depth = 2 (city -> line -> station)
                entry = {
                    "id": station_id,
                    "station_name": station_name,
                    "city_id": city_id,
                    "city_name": city_name,
                    "line_id": line_id,
                    "line_name": line_name,
                    "path": f"{city_name} > {line_name} > {station_name}",
                    "depth": 2,
                }
                norm = normalize_name(station_name)

                if norm:
                    name_map[norm].append(entry)
                    all_names.append(norm)

                combo1 = normalize_name(f"{city_name} {station_name}")

                if combo1 and combo1 != norm:
                    name_map[combo1].append(entry)
                    all_names.append(combo1)

                combo2 = normalize_name(f"{line_name} {station_name}")

                if combo2 and combo2 != norm and combo2 != combo1:
                    name_map[combo2].append(entry)
                    all_names.append(combo2)


    all_names = sorted(set(all_names))
    return name_map, all_names



def choose_best_candidate(candidates: list[dict[str, Any]]) -> list[str]:
    '''
    возвращает список id лучших кандидатов среди candidates.
    берет максимальную глубину (в нашем случае все станции depth=2),
    если несколько одинаковых — возвращает уникальные id.
    '''
    if not candidates:
        return []

    max_depth = max(c["depth"] for c in candidates)
    best = [c for c in candidates if c["depth"] == max_depth]

    return list({c["id"] for c in best})



class MetroResolver:
    def __init__(self, name_map: dict[str, list[dict[str, Any]]], all_names: list[str]) -> None:
        self.name_map = name_map
        self.all_names = all_names


    def resolve(self, user_input: str | None) -> list[str]:
        '''
        преобразует строку пользователя в список station ids (например "8.189").
        если ничего не найдено — возвращает пустой список.
        '''
        if not user_input:
            return []

        norm = normalize_name(user_input)
        if not norm:
            return []

        # точное совпадение
        if norm in self.name_map:
            return choose_best_candidate(self.name_map[norm])

        # частями (например "москва новокосино" -> "новокосино")
        parts = [p for p in norm.split(' ') if p]
        for part in reversed(parts):
            if part in self.name_map:
                return choose_best_candidate(self.name_map[part])

        matches = difflib.get_close_matches(norm, self.all_names, n=3, cutoff=0.75)

        if matches:
            best_norm = matches[0]
            return choose_best_candidate(self.name_map.get(best_norm, []))

        return []



def load_metro_resolver_from_file(path: str) -> MetroResolver:
    p = pathlib.Path(path)
    raw = json.loads(p.read_text(encoding='utf-8'))
    name_map, all_names = build_metro_index(raw)

    return MetroResolver(name_map, all_names)